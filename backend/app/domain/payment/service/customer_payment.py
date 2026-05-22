"""customer 의 /payment/init / /payment/confirm — 다도메인 오케스트레이션 진입점."""
from typing import List, Optional
from math import ceil
from fastapi import BackgroundTasks
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field

from app.util.id_generator import generate_payment_id
from app.domain.seller.service.seller_store_read import SellerStoreReadService
from app.domain.seller.service.seller_product import SellerProductService
from app.domain.seller.service.exception import (
    ProductStockConflictError,
    ProductStockInsufficientError,
)
from app.domain.payment.service.store_payment_info import StorePaymentInfoService
from app.domain.payment.service.payment_gateway import PaymentGatewayService
from app.domain.payment.service.exception import (
    PaymentInfoIncompleteError,
    PaymentInfoMissingError,
    PaymentNotFoundError,
    PaymentOwnershipMismatchError,
    PaymentRefundError,
    PaymentTimeoutError,
    PaymentVerificationError,
    PickupTimeEndedError,
    ProductNotFoundError,
    StockConflictError,
    StockInsufficientError,
    StoreNotOpenError,
)
from app.domain.payment.schema.customer_payment import (
    PaymentInitResponse,
    PaymentResponse,
)
from app.domain.order.service.order_query import OrderQueryService
from app.domain.customer.service.customer_profile import CustomerProfileService
from app.database.session import UnitOfWork, transactional
from app.core.portone import PortOnePaymentStatus, PortOneTransientError
from app.core.logger import get_logger
from app.core.email.notifier import send_reservation_email


@dataclass
class SweepResult:
    """``sweep_expired_carts`` 의 결과 — worker 가 이메일 발송 + 로깅에 사용."""
    finalized: int = 0          # PAID → 주문 자동 생성
    cancelled: int = 0          # 결제 안 됨 / 실패 / 금액 불일치 → cart + 재고 정리
    transient: int = 0          # PortOne 5xx/timeout — 다음 sweep 으로 미룸
    finalized_customer_emails: List[str] = field(default_factory=list)


_KST = timezone(timedelta(hours=9))
_PAYMENT_TIMEOUT = timedelta(minutes=5)
logger = get_logger("payment.service.customer_payment")


class CustomerPaymentService:
    """결제 init/confirm 의 오케스트레이션.

    여러 도메인 service 를 호출하지만 ContextVar 기반 `@transactional` 덕분에 한 진입점에서
    트랜잭션이 열리면 nested service 호출이 모두 같은 세션을 공유한다.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        seller_store_read_service: SellerStoreReadService,
        seller_product_service: SellerProductService,
        store_payment_info_service: StorePaymentInfoService,
        payment_gateway_service: PaymentGatewayService,
        order_query_service: OrderQueryService,
        customer_profile_service: CustomerProfileService,
    ):
        self.uow = uow
        self.seller_store_read_service = seller_store_read_service
        self.seller_product_service = seller_product_service
        self.store_payment_info_service = store_payment_info_service
        self.payment_gateway_service = payment_gateway_service
        self.order_query_service = order_query_service
        self.customer_profile_service = customer_profile_service


    @transactional
    async def init_payment(
        self, *, customer_email: str, product_id: str, quantity: int,
    ) -> PaymentInitResponse:
        """결제 init — 사전 검증 + 재고 차감 + cart 생성 (전부 한 tx).

        한 tx 로 묶는 이유: 재고 차감 후 cart 생성 전 프로세스가 비정상 종료되면
        재고만 commit 되고 sweeper 가 복구할 cart 가 없어 재고 영구 손실. atomic 보장.

        실패 분기:
          - 사전 검증 (product/store/stock) — DB 변경 전이므로 그냥 raise.
          - 재고 차감 / payment_info 조회 / cart 생성 중 어디서든 raise →
            ``@transactional`` 이 outer tx 를 롤백 → 차감된 재고 자동 복원.
        """
        product = await self.seller_product_service.find_product(product_id)
        if product is None:
            raise ProductNotFoundError("상품을 찾을 수 없습니다")

        await self._assert_pickup_available(product.store_id)

        if product.current_stock < quantity:
            raise StockInsufficientError(
                f"재고가 부족합니다. 현재 재고: {product.current_stock}개",
            )

        # 결제 timeout 은 DB 컬럼 (cart_items.expires_at) 으로 추적 — sweeper worker 가
        # 만료된 cart 를 분산-안전하게 처리. APScheduler in-memory job 의 단일 노드 한계를
        # 회피하기 위한 패턴.
        payment_id = generate_payment_id()
        total_amount = _total_amount(price=product.price, sale=product.sale, quantity=quantity)
        expires_at = datetime.now(timezone.utc) + _PAYMENT_TIMEOUT

        # 임시 재고 차감 → payment_info 조회 → cart 생성. 어느 단계든 raise 시
        # @transactional 롤백으로 전부 원자적 취소.
        try:
            await self.seller_product_service.consume_purchased_stock(
                product_id=product_id, quantity=quantity,
            )
        except ProductStockInsufficientError:
            raise StockInsufficientError("재고가 부족합니다")
        except ProductStockConflictError:
            raise StockConflictError("재고 차감 중 충돌이 발생했습니다")

        payment_info = await self.store_payment_info_service.get_complete_by_store(
            product.store_id,
        )

        await self.order_query_service.create_cart_item(
            payment_id=payment_id,
            product_id=product_id,
            customer_id=customer_email,
            quantity=quantity,
            price=product.price,
            sale=product.sale,
            total_amount=total_amount,
            expires_at=expires_at,
        )

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
        """브라우저 confirm 진입점. ownership/pickup 사전 검증 후 _finalize_payment 위임.

        _finalize_payment 가 내부에서 cart 를 FOR UPDATE lock 으로 재조회 → confirm/sweeper
        동시 진입 시 직렬화. 사전 검증과 lock 안의 재조회 사이에서 cart 가 사라졌다면
        다른 흐름이 이미 처리한 것 — caller 에 PaymentNotFoundError.
        """
        # 사전 검증 — 빠르게 실패. lock 잡기 전에 가벼운 검증.
        cart_item = await self.order_query_service.get_cart_item(payment_id)
        if cart_item is None:
            raise PaymentNotFoundError("결제 정보를 찾을 수 없습니다")
        if cart_item.customer_id != customer_email:
            raise PaymentOwnershipMismatchError("결제에 대한 권한이 없습니다")
        if cart_item.expires_at <= datetime.now(timezone.utc):
            raise PaymentTimeoutError("결제 시간이 만료되었습니다.")

        product = await self.seller_product_service.find_product(cart_item.product_id)
        if product is None:
            raise ProductNotFoundError("상품 정보를 찾을 수 없습니다")
        await self._assert_pickup_available(product.store_id)

        finalized = await self._finalize_payment(payment_id=payment_id)
        if not finalized:
            # lock 내부에서 cart 가 사라졌음 (다른 흐름이 먼저 처리).
            raise PaymentNotFoundError("결제 정보를 찾을 수 없습니다")

        # 예약 완료 이메일은 RDB 트랜잭션과 무관 — background.
        background_tasks.add_task(send_reservation_email, customer_email)

        return PaymentResponse(payment_id=payment_id)


    @transactional
    async def _finalize_payment(self, *, payment_id: str) -> bool:
        """결제 진실 검증 + 주문 생성 + cart 삭제. confirm 의 핵심 finalize.

        sweep_expired_carts 는 만료된 cart 만 다루므로 이 메서드를 호출하지 않고 별도
        `_sweep_cart` 경로를 사용한다 (verify 가 sweep 에선 fetch_status 로 대체됨).

        멱등성/원자성:
          1) cart 를 `FOR UPDATE` 로 lock — 같은 payment_id 의 동시 진입 직렬화.
          2) cart 가 None 이면 다른 흐름이 이미 처리 → False 반환 (NoOp 신호).
          3) verify (외부 PortOne 호출) → 같은 트랜잭션 안. lock 유지로 sweeper 차단.
          4) verify 성공 후 order 생성 + cart 삭제 — IntegrityError 가 발생할 여지가 없음
             (다른 흐름은 lock 으로 대기 → 그때는 cart 이미 삭제됨).

        Returns:
            True  — finalize 성공.
            False — cart 가 lock 시점에 이미 없음 (다른 흐름이 먼저 처리). caller 가 NoOp 처리.

        실패 흐름:
          - verify 실패: 돈 안 빠짐 → cart 삭제 + 재고 복구 (같은 tx).
          - verify 성공 후 persist 실패: 돈 빠짐 → tx 롤백 → 환불 + 복구 (별도 tx).
        """
        cart_item = await self.order_query_service.lock_cart_item(payment_id)
        if cart_item is None:
            return False

        product = await self.seller_product_service.find_product(cart_item.product_id)
        if product is None:
            # cart 는 있는데 product 가 없는 비정상 상태. cart 만 정리.
            logger.error(
                "[CRITICAL] finalize 시 product 없음 payment_id={} product_id={}",
                payment_id, cart_item.product_id,
            )
            await self.order_query_service.delete_cart_item(payment_id)
            return True

        payment_info = await self.store_payment_info_service.get_complete_by_store(
            product.store_id,
        )
        preference = await self.customer_profile_service.get_preference_snapshot(
            cart_item.customer_id,
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
            # 돈 안 빠짐 (또는 빠졌어도 amount 조작 등 우리 책임 아닌 케이스).
            # cart + 재고는 같은 tx 에서 정리. tx commit 으로 cart 사라지면 멱등 보장.
            await self._safe_restore_stock(cart_item.product_id, cart_item.quantity)
            await self.order_query_service.delete_cart_item(payment_id)
            raise

        try:
            # order 생성 + cart 삭제 — 같은 tx. lock 덕분에 다른 흐름은 대기 중.
            await self.order_query_service.create_order_from_cart(
                cart_item=cart_item, preference_snapshot=preference,
            )
            await self.order_query_service.delete_cart_item(payment_id)
        except Exception:
            # tx 롤백 후 보상 — verify 는 외부에서 성공한 상태이므로 환불 필요.
            logger.exception(
                "[CRITICAL] verify 성공 후 persist 실패 — 환불 시도 payment_id={}",
                payment_id,
            )
            await self._rollback_after_paid(
                payment_id=payment_id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                secret_key=payment_info.portone_secret_key,
            )
            raise
        return True


    # ───────── sweeper 진입점 ─────────


    @transactional
    async def sweep_expired_carts(self, *, limit: int = 100) -> SweepResult:
        """만료된 cart_item 을 batch 로 처리.

        webhook 을 안 쓰므로 본 sweeper 가 confirm 누락의 안전망 역할:
          - 사용자가 결제 완료했지만 confirm 호출이 안 온 경우 (브라우저 종료 등)
            → PortOne 진위 조회 후 PAID 면 주문 자동 생성 (= confirm 효과).
          - 사용자가 결제 안 했거나 실패 → 재고 복구 + cart 삭제.
          - PortOne 일시 장애 → 해당 cart 만 건너뛰고 다음 sweep 에서 재시도.

        호출 주기: 1분 (``app.domain.payment.worker.expire_cart_items``).
        다중 노드 동시 발화 시 ``FOR UPDATE SKIP LOCKED`` 로 row 단위 분산 — 외부 tx 가
        살아있는 동안 (= 본 함수가 return 할 때까지) 다른 sweeper 는 같은 row 를 건드리지
        못한다.

        각 cart 처리는 SAVEPOINT 로 격리 — 한 cart 의 DB 오류가 batch 전체를
        ``InFailedSqlTransaction`` 으로 망가뜨리지 못하게.
        """
        expired = await self.order_query_service.claim_expired_carts_for_processing(
            now=datetime.now(timezone.utc), limit=limit,
        )
        result = SweepResult()
        if not expired:
            return result

        for cart in expired:
            try:
                outcome = await self._sweep_cart(cart)
            except PortOneTransientError as e:
                # PortOne 5xx — 다음 sweep 에서 재시도. cart 는 그대로 유지.
                result.transient += 1
                logger.warning(
                    "sweep — PortOne 일시 장애로 미룸 payment_id={}: {}",
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
            else:  # "cancelled"
                result.cancelled += 1
        return result


    async def _sweep_cart(self, cart) -> str:
        """SAVEPOINT 안에서 cart 1건 처리.

        Returns:
            "finalized" — PortOne 측 PAID 확인 → 주문 자동 생성.
            "cancelled" — 결제 기록 없음 / PAID 아님 / 금액 불일치 → cart + 재고 정리.

        Raises:
            ``PortOneTransientError`` — caller 가 다음 sweep 으로 미룸.
        """
        product = await self.seller_product_service.find_product(cart.product_id)
        if product is None:
            # broken state — cart 만 정리.
            async with self._session.begin_nested():
                await self.order_query_service.delete_cart_item(cart.payment_id)
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
            # 가게의 결제 설정이 빠짐 — 검증 불가. cart 손대지 않고 운영자에게 알람.
            # raise 가 아닌 transient 로 흘려보내 sweep 결과 카운터에 잡히게 한다.
            logger.error(
                "[CRITICAL] sweep — store payment_info 누락, 수동 조치 필요 payment_id={} store_id={}",
                cart.payment_id, product.store_id,
            )
            raise PortOneTransientError(
                f"store {product.store_id} payment_info incomplete",
            )

        # 외부 PortOne 진위 조회. transient 는 그대로 raise → caller catch.
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
            # 사용자가 결제 완료 — confirm 누락 안전망. 주문 자동 생성.
            preference = await self.customer_profile_service.get_preference_snapshot(
                cart.customer_id,
            )
            async with self._session.begin_nested():
                await self.order_query_service.create_order_from_cart(
                    cart_item=cart, preference_snapshot=preference,
                )
                await self.order_query_service.delete_cart_item(cart.payment_id)
            logger.info(
                "sweep — confirm 누락 결제 자동 finalize payment_id={} customer={}",
                cart.payment_id, cart.customer_id,
            )
            return "finalized"

        # 결제 안 됨 / 실패 / 금액 변조 — 재고 복구 + cart 삭제. 환불은 status PAID 가
        # 아니므로 불필요 (결제가 실제로 일어나지 않은 상태).
        if payment is not None and payment.status == PortOnePaymentStatus.PAID:
            # amount 만 다른 경우 — tampering 가능성. CRITICAL 로깅 후 정리.
            logger.error(
                "[CRITICAL] sweep — PAID amount 불일치 expected={} got={} payment_id={}",
                cart.total_amount, payment.total_amount, cart.payment_id,
            )
        # restore_purchased_stock 가 raise 하면 SAVEPOINT 가 delete 와 함께 롤백한다 —
        # 재고만 손실되고 cart 가 사라지는 사고 방지. caller 가 Exception 으로 잡아
        # 다음 sweep 으로 미룬다.
        async with self._session.begin_nested():
            await self.seller_product_service.restore_purchased_stock(
                product_id=cart.product_id, quantity=cart.quantity,
            )
            await self.order_query_service.delete_cart_item(cart.payment_id)
        return "cancelled"


    # ───────── private ─────────


    async def _assert_pickup_available(self, store_id: str) -> None:
        op = await self.seller_store_read_service.get_today_operation(store_id)
        if op is None:
            raise StoreNotOpenError("가게가 오늘은 영업하지 않습니다")
        if not op.is_currently_open:
            raise StoreNotOpenError("가게가 현재 영업 중이 아닙니다")
        if datetime.now(_KST).time() > op.pickup_end_time:
            raise PickupTimeEndedError(
                f"픽업 시간이 종료되었습니다. 픽업 종료 시간: "
                f"{op.pickup_end_time.strftime('%H:%M')}",
            )


    async def _safe_restore_stock(self, product_id: str, quantity: int) -> None:
        """재고 복구 — 예외는 swallow + critical 로깅.

        outer tx 가 있으면 (verify 실패 분기) 같은 세션에 참여, 없으면 (rollback_after_paid)
        ``restore_purchased_stock`` 의 ``@transactional`` 이 새 tx 를 열어 commit.
        """
        try:
            await self.seller_product_service.restore_purchased_stock(
                product_id=product_id, quantity=quantity,
            )
        except Exception:
            logger.exception(
                "[CRITICAL] 재고 복구 실패 product_id={} quantity={}", product_id, quantity,
            )


    async def _safe_delete_cart(self, payment_id: str) -> None:
        try:
            await self.order_query_service.delete_cart_item(payment_id)
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
        """결제 성공 후 내부 처리 실패 → 환불 + 복구. 부분 실패는 모두 critical 로깅.

        reason 은 고정 문구 (내부 메시지 leak 방지). 운영자 알람은 [CRITICAL] 마커 의존.
        """
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
        await self._safe_restore_stock(product_id, quantity)
        await self._safe_delete_cart(payment_id)


def _total_amount(*, price: int, sale: Optional[int], quantity: int) -> int:
    """sale 이 있으면 단가를 100원 단위로 올림 후 곱."""
    if sale:
        discounted = price * (100 - sale) / 100
        unit = ceil(discounted / 100) * 100
        return unit * quantity
    return price * quantity
