"""customer 의 /payment/init / /payment/confirm — payment-backend 의 핵심 오케스트레이션.

MSA 분리 후 변경점:
  - product/stock 조회 + 차감/복원은 HTTP 로 main-backend 호출.
  - order 생성도 HTTP 로 main-backend 호출 (멱등 키 = payment_id).
  - cart_items 는 payment-backend 자체 DB — FOR UPDATE / SKIP LOCKED 동시성 의미 유지.

동시성:
  - `_finalize_payment` 와 `sweep_expired_carts` 는 자체 ``@transactional`` — 그 안에서
    cart_item_service.lock / claim_expired_for_processing 가 외부 tx 에 참여해 lock 이 함수
    전체 동안 유지된다. 원본 single-process 와 동일한 직렬화 의미.
  - HTTP 호출 동안 payment-backend DB 세션 + cart row lock 이 잡혀 있다 — connection pool
    부담은 1차 cut 트레이드오프. main-backend 측 stock_operation_log 가 stock 조작 멱등을 보장
    하므로, 향후 cart lock 제거 + 더 짧은 tx 로 리팩토링 시에도 stock 정합성은 유지된다.

원자성:
  - init: stock(HTTP) 과 cart(local) 가 다른 시스템. cart 생성 실패 시 stock 보상 호출.
  - finalize 후처리 실패 분기 :
      4xx (OrderCreateFailedError) → main-backend 가 명확히 거부 → 환불 + 보상.
      5xx (BackendUnavailableError) → main-backend commit 여부 불명 → **환불 금지**, cart 유지,
                                       sweep 이 멱등 retry. 환불하면 main-backend 에 commit 된
                                       주문이 외로워지는 사고가 난다.
"""
from typing import List, Optional
from math import ceil
from fastapi import BackgroundTasks
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field

from app.util.id_generator import generate_payment_id
from app.domain.payment.service.store_payment_info import StorePaymentInfoService
from app.domain.payment.service.payment_gateway import PaymentGatewayService
from app.domain.payment.service.cart_item import CartItemService
from app.domain.payment.service.exception import (
    BackendUnavailableError,
    OrderCreateFailedError,
    PaymentInfoIncompleteError,
    PaymentInfoMissingError,
    PaymentNotFoundError,
    PaymentOwnershipMismatchError,
    PaymentRefundError,
    PaymentTimeoutError,
    PaymentVerificationError,
    PickupTimeEndedError,
    ProductNotFoundError,
    StockInsufficientError,
    StoreNotOpenError,
)
from app.domain.payment.schema.customer_payment import (
    PaymentInitResponse,
    PaymentResponse,
)
from app.database.session import UnitOfWork, transactional
from app.core.internal_client.seller import InternalSellerClient
from app.core.internal_client.order import InternalOrderClient
from app.core.portone import PortOnePaymentStatus, PortOneTransientError
from app.core.logger import get_logger
from app.core.email.notifier import send_reservation_email


@dataclass
class SweepResult:
    finalized: int = 0
    cancelled: int = 0
    transient: int = 0
    finalized_customer_emails: List[str] = field(default_factory=list)


_KST = timezone(timedelta(hours=9))
_PAYMENT_TIMEOUT = timedelta(minutes=5)
logger = get_logger("payment.service.customer_payment")


class CustomerPaymentService:

    def __init__(
        self,
        uow: UnitOfWork,
        store_payment_info_service: StorePaymentInfoService,
        payment_gateway_service: PaymentGatewayService,
        cart_item_service: CartItemService,
        internal_seller_client: InternalSellerClient,
        internal_order_client: InternalOrderClient,
    ):
        self.uow = uow
        self.store_payment_info_service = store_payment_info_service
        self.payment_gateway_service = payment_gateway_service
        self.cart_item_service = cart_item_service
        self.internal_seller_client = internal_seller_client
        self.internal_order_client = internal_order_client


    async def init_payment(
        self, *, customer_email: str, product_id: str, quantity: int,
    ) -> PaymentInitResponse:
        """결제 init — main-backend stock 차감 + payment-backend cart 생성.

        한 트랜잭션이 아님 (다른 시스템). 순서:
          1) main-backend product 조회 + pickup 검증 + 재고 검증 (read)
          2) payment-backend payment_info 조회 + payment_id 생성
          3) main-backend consume_stock(payment_id 멱등) — write
          4) payment-backend cart_items INSERT — write
          5) (4) 실패 시 main-backend restore_stock(payment_id) best-effort
        """
        product = await self.internal_seller_client.find_product(product_id)
        if product is None:
            raise ProductNotFoundError("상품을 찾을 수 없습니다")

        await self._assert_pickup_available(product.store_id)

        if product.current_stock < quantity:
            raise StockInsufficientError(
                f"재고가 부족합니다. 현재 재고: {product.current_stock}개",
            )

        payment_info = await self.store_payment_info_service.get_complete_by_store(
            product.store_id,
        )

        payment_id = generate_payment_id()
        total_amount = _total_amount(price=product.price, sale=product.sale, quantity=quantity)
        expires_at = datetime.now(timezone.utc) + _PAYMENT_TIMEOUT

        # main-backend 재고 차감 (payment_id 멱등 — 일시 장애 시 다시 호출돼도 동일 결과).
        await self.internal_seller_client.consume_stock(
            payment_id=payment_id, product_id=product_id, quantity=quantity,
        )

        # cart 생성. 실패 시 stock 보상 호출 + raise.
        try:
            await self.cart_item_service.create(
                payment_id=payment_id,
                product_id=product_id,
                customer_id=customer_email,
                quantity=quantity,
                price=product.price,
                sale=product.sale,
                total_amount=total_amount,
                expires_at=expires_at,
            )
        except Exception:
            logger.exception(
                "[CRITICAL] cart 생성 실패 — stock 보상 호출 payment_id={}", payment_id,
            )
            try:
                await self.internal_seller_client.restore_stock(
                    payment_id=payment_id, product_id=product_id, quantity=quantity,
                )
            except Exception:
                logger.exception(
                    "[CRITICAL] stock 보상 호출도 실패 — 운영자 수동 조치 필요 payment_id={}",
                    payment_id,
                )
            raise

        return PaymentInitResponse(
            payment_id=payment_id,
            channel_id=payment_info.portone_channel_id,
            store_id=payment_info.portone_store_id,
            quantity=quantity,
            price=product.price,
            sale=product.sale,
            total_amount=total_amount,
        )


    async def confirm_payment(
        self,
        *,
        customer_email: str,
        payment_id: str,
        background_tasks: BackgroundTasks,
    ) -> PaymentResponse:
        """브라우저 confirm — finalize 위임 + 이메일 background task."""
        # 사전 검증 — lock 잡기 전 경량 체크.
        cart_item = await self.cart_item_service.get(payment_id)
        if cart_item is None:
            raise PaymentNotFoundError("결제 정보를 찾을 수 없습니다")
        if cart_item.customer_id != customer_email:
            raise PaymentOwnershipMismatchError("결제에 대한 권한이 없습니다")
        if cart_item.expires_at <= datetime.now(timezone.utc):
            raise PaymentTimeoutError("결제 시간이 만료되었습니다.")

        product = await self.internal_seller_client.find_product(cart_item.product_id)
        if product is None:
            raise ProductNotFoundError("상품 정보를 찾을 수 없습니다")
        await self._assert_pickup_available(product.store_id)

        finalized = await self._finalize_payment(payment_id=payment_id)
        if not finalized:
            raise PaymentNotFoundError("결제 정보를 찾을 수 없습니다")

        background_tasks.add_task(send_reservation_email, customer_email)
        return PaymentResponse(payment_id=payment_id)


    @transactional
    async def _finalize_payment(self, *, payment_id: str) -> bool:
        """cart lock + PortOne verify + order 생성 (HTTP) + cart 삭제.

        ``@transactional`` 로 외부 tx 를 열어 cart_item_service.lock / delete 가 모두 참여한다.
        FOR UPDATE 잠금이 PortOne 호출 + main-backend create_order HTTP 동안 유지되어 confirm/sweep
        동시 진입을 직렬화한다 (원본과 동일 의미).

        실패 분기:
          - PaymentVerificationError: 돈 안 빠짐. cart 삭제 + stock 복원 후 raise.
            (delete/restore 가 outer tx 에 참여 → raise 로 tx 롤백 → sweep 이 fetch_status
            CANCELLED 로 다시 정리. PortOne 환불은 일어나지 않는다.)
          - OrderCreateFailedError (4xx): main-backend 가 명확히 거부. PortOne 환불 + 보상.
          - BackendUnavailableError (5xx/네트워크): main-backend commit 여부 불명. **환불 금지**.
            cart 유지 (raise 로 outer tx 롤백 → cart delete 가 안 일어남). sweep 이 멱등 retry
            로 자동 복원. 환불 시 main-backend commit 된 주문이 외로워지는 사고 방지.
        """
        cart_item = await self.cart_item_service.lock(payment_id)
        if cart_item is None:
            return False

        product = await self.internal_seller_client.find_product(cart_item.product_id)
        if product is None:
            logger.error(
                "[CRITICAL] finalize 시 product 없음 payment_id={} product_id={}",
                payment_id, cart_item.product_id,
            )
            await self.cart_item_service.delete(payment_id)
            return True

        payment_info = await self.store_payment_info_service.get_complete_by_store(
            product.store_id,
        )

        try:
            payment = await self.payment_gateway_service.verify(
                payment_id=payment_id,
                secret_key=payment_info.portone_secret_key,
                expected_amount=cart_item.total_amount,
            )
            logger.info(
                "결제 검증 성공 — customer={}, method={}, amount={}",
                cart_item.customer_id, payment.payment_method, payment.total_amount,
            )
        except PaymentVerificationError:
            # 돈 안 빠짐. cart + stock 정리. 같은 outer tx 안의 cart 삭제는 raise 로 롤백되지만
            # restore_stock 은 HTTP (별도 tx in main-backend) — 적용됨. raise 후 outer tx 롤백되어
            # cart 가 남으면 sweep 이 CANCELLED 로 인지하고 restore + delete 처리.
            # main-backend 의 (payment_id, "restore") stock_operation_log PK 로 sweep restore 가
            # 중복 호출되어도 한 번만 적용 — 재고 과복원 없음.
            await self._safe_restore_stock(
                payment_id=payment_id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
            )
            await self._safe_delete_cart(payment_id)
            raise

        try:
            # order HTTP 생성 (payment_id 멱등). 성공 시 cart 삭제 (outer tx 안).
            await self.internal_order_client.create_order_from_cart(
                payment_id=cart_item.payment_id,
                product_id=cart_item.product_id,
                customer_id=cart_item.customer_id,
                quantity=cart_item.quantity,
                price=cart_item.price,
                sale=cart_item.sale,
                total_amount=cart_item.total_amount,
            )
            await self.cart_item_service.delete(payment_id)
        except OrderCreateFailedError:
            # 4xx — main-backend 가 명확히 거부 (예: validation 실패). 환불 + 보상.
            logger.exception(
                "[CRITICAL] verify 성공 후 order 생성 거부 (4xx) — 환불 시도 payment_id={}",
                payment_id,
            )
            await self._rollback_after_paid(
                payment_id=payment_id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                secret_key=payment_info.portone_secret_key,
            )
            raise
        except BackendUnavailableError:
            # 5xx / 네트워크 — main-backend commit 여부 불명. 환불하면 commit 된 주문이
            # 외로워질 위험. cart 그대로 두고 raise → outer tx 롤백 (cart 삭제 안 됨).
            # sweep 이 다음 tick 에 fetch_status PAID 확인 + create_order 멱등 호출로 복원.
            logger.exception(
                "[CRITICAL] verify 성공 후 order 생성 transient 실패 — sweep 재처리 대기 "
                "payment_id={}",
                payment_id,
            )
            raise
        return True


    @transactional
    async def sweep_expired_carts(self, *, limit: int = 100) -> SweepResult:
        """만료된 cart_item batch 처리 — confirm 누락 안전망.

        ``@transactional`` 로 outer tx 를 열어 cart_item_service.claim_expired_for_processing
        의 SKIP LOCKED 잠금이 sweep 전체 동안 유지된다. 다른 노드의 sweep tick 은 이 행을 건너뛴다.

        각 cart 처리는 `begin_nested()` SAVEPOINT 로 격리 — 한 cart 의 DB 오류가 batch 전체를
        ``InFailedSqlTransaction`` 으로 망가뜨리지 못하게.
        """
        expired = await self.cart_item_service.claim_expired_for_processing(
            now=datetime.now(timezone.utc), limit=limit,
        )
        result = SweepResult()
        if not expired:
            return result

        for cart in expired:
            try:
                outcome = await self._sweep_cart(cart)
            except PortOneTransientError as e:
                result.transient += 1
                logger.warning(
                    "sweep — PortOne 일시 장애로 미룸 payment_id={}: {}",
                    cart.payment_id, e,
                )
                continue
            except BackendUnavailableError as e:
                result.transient += 1
                logger.warning(
                    "sweep — main-backend 일시 장애로 미룸 payment_id={}: {}",
                    cart.payment_id, e,
                )
                continue
            except Exception:
                logger.exception(
                    "[CRITICAL] sweep — 예측 못한 오류 payment_id={}", cart.payment_id,
                )
                continue

            if outcome == "finalized":
                result.finalized += 1
                result.finalized_customer_emails.append(cart.customer_id)
            else:
                result.cancelled += 1
        return result


    async def _sweep_cart(self, cart) -> str:
        """cart 1건 처리. outer @transactional 안에서 동작 — DB write 는 SAVEPOINT 로 격리.

        Returns:
            "finalized" — PortOne PAID 확인 → main-backend order 생성 (멱등).
            "cancelled" — 결제 기록 없음 / PAID 아님 / 금액 불일치 → restore + cart 삭제.
            (또는 main-backend 4xx 시 환불 + cancelled 로 종료.)

        Raises:
            PortOneTransientError: PortOne 5xx — caller 가 다음 sweep 으로 미룸.
            BackendUnavailableError: main-backend 5xx/네트워크 — caller 가 다음 sweep 으로 미룸.
        """
        product = await self.internal_seller_client.find_product(cart.product_id)
        if product is None:
            async with self._session.begin_nested():
                await self.cart_item_service.delete(cart.payment_id)
            logger.error(
                "[CRITICAL] sweep — product 없음 payment_id={} product_id={}",
                cart.payment_id, cart.product_id,
            )
            return "cancelled"

        try:
            payment_info = await self.store_payment_info_service.get_complete_by_store(
                product.store_id,
            )
        except (PaymentInfoMissingError, PaymentInfoIncompleteError):
            logger.error(
                "[CRITICAL] sweep — store payment_info 누락, 수동 조치 필요 payment_id={} store_id={}",
                cart.payment_id, product.store_id,
            )
            raise PortOneTransientError(
                f"store {product.store_id} payment_info incomplete",
            )

        # PortOne 진위 조회 — transient 는 그대로 raise → caller catch.
        payment = await self.payment_gateway_service.fetch_status(
            payment_id=cart.payment_id,
            secret_key=payment_info.portone_secret_key,
        )

        is_paid = (
            payment is not None
            and payment.status == PortOnePaymentStatus.PAID
            and payment.total_amount == cart.total_amount
        )

        if is_paid:
            # confirm 누락 → main-backend order 생성 (payment_id 멱등). cart 삭제.
            try:
                await self.internal_order_client.create_order_from_cart(
                    payment_id=cart.payment_id,
                    product_id=cart.product_id,
                    customer_id=cart.customer_id,
                    quantity=cart.quantity,
                    price=cart.price,
                    sale=cart.sale,
                    total_amount=cart.total_amount,
                )
            except OrderCreateFailedError:
                # 4xx — main-backend 가 명확히 거부. PAID 인데 order 생성 불가 — 환불 처리.
                logger.exception(
                    "[CRITICAL] sweep — PAID order 생성 거부 (4xx), 환불 처리 payment_id={}",
                    cart.payment_id,
                )
                await self._rollback_after_paid(
                    payment_id=cart.payment_id,
                    product_id=cart.product_id,
                    quantity=cart.quantity,
                    secret_key=payment_info.portone_secret_key,
                )
                return "cancelled"
            # BackendUnavailableError 는 raise — caller transient 처리.

            async with self._session.begin_nested():
                await self.cart_item_service.delete(cart.payment_id)
            logger.info(
                "sweep — confirm 누락 결제 자동 finalize payment_id={} customer={}",
                cart.payment_id, cart.customer_id,
            )
            return "finalized"

        if payment is not None and payment.status == PortOnePaymentStatus.PAID:
            # amount 만 다른 경우 — tampering 가능성. CRITICAL 로깅 후 정리.
            logger.error(
                "[CRITICAL] sweep — PAID amount 불일치 expected={} got={} payment_id={}",
                cart.total_amount, payment.total_amount, cart.payment_id,
            )
        # 결제 안 됨 / 실패 / 금액 변조 — stock 복구 + cart 삭제. PortOne 환불은 PAID 가
        # 아니므로 불필요. restore 는 HTTP, delete 는 SAVEPOINT 안에서.
        await self._safe_restore_stock(
            payment_id=cart.payment_id,
            product_id=cart.product_id,
            quantity=cart.quantity,
        )
        async with self._session.begin_nested():
            await self.cart_item_service.delete(cart.payment_id)
        return "cancelled"


    # ───────── private ─────────


    async def _assert_pickup_available(self, store_id: str) -> None:
        op = await self.internal_seller_client.get_today_operation(store_id)
        if op is None:
            raise StoreNotOpenError("가게가 오늘은 영업하지 않습니다")
        if not op.is_currently_open:
            raise StoreNotOpenError("가게가 현재 영업 중이 아닙니다")
        # pickup_end_time 은 HH:MM:SS 문자열 — KST 현재 시각과 비교.
        now_kst = datetime.now(_KST).strftime("%H:%M:%S")
        if now_kst > op.pickup_end_time:
            raise PickupTimeEndedError(
                f"픽업 시간이 종료되었습니다. 픽업 종료 시간: {op.pickup_end_time[:5]}",
            )


    async def _safe_restore_stock(
        self, *, payment_id: str, product_id: str, quantity: int,
    ) -> None:
        try:
            await self.internal_seller_client.restore_stock(
                payment_id=payment_id, product_id=product_id, quantity=quantity,
            )
        except Exception:
            logger.exception(
                "[CRITICAL] 재고 복구 실패 payment_id={} product_id={} quantity={}",
                payment_id, product_id, quantity,
            )


    async def _safe_delete_cart(self, payment_id: str) -> None:
        try:
            await self.cart_item_service.delete(payment_id)
        except Exception:
            logger.exception(
                "[CRITICAL] cart 삭제 실패 payment_id={}", payment_id,
            )


    async def _rollback_after_paid(
        self,
        *,
        payment_id: str,
        product_id: str,
        quantity: int,
        secret_key: Optional[str],
    ) -> None:
        if secret_key:
            try:
                await self.payment_gateway_service.refund(
                    payment_id=payment_id,
                    secret_key=secret_key,
                    reason="주문 생성 실패로 인한 자동 환불",
                )
            except PaymentRefundError:
                logger.exception(
                    "[CRITICAL] 환불 실패 — 운영자 수동 처리 필요 payment_id={}", payment_id,
                )
        else:
            logger.error(
                "[CRITICAL] secret_key 없음 — 환불 불가 payment_id={}", payment_id,
            )
        await self._safe_restore_stock(
            payment_id=payment_id, product_id=product_id, quantity=quantity,
        )
        await self._safe_delete_cart(payment_id)


def _total_amount(*, price: int, sale: Optional[int], quantity: int) -> int:
    """sale 이 있으면 단가를 100원 단위로 올림 후 곱."""
    if sale:
        discounted = price * (100 - sale) / 100
        unit = ceil(discounted / 100) * 100
        return unit * quantity
    return price * quantity
