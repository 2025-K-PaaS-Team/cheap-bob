"""customer 의 /payment/init / /payment/confirm — 다도메인 오케스트레이션 진입점."""
from typing import Optional
from loguru import logger
from fastapi import BackgroundTasks
from datetime import datetime, timedelta, timezone

from app.util.id_generator import generate_payment_id
from app.domain.seller.service.seller_store_read import SellerStoreReadService
from app.domain.seller.service.seller_product import SellerProductService
from app.domain.seller.service.exception import (
    ProductStockConflictError,
    ProductStockInsufficientError,
)
from app.domain.payment.service.store_payment_info import StorePaymentInfoService
from app.domain.payment.service.payment_scheduler import PaymentSchedulerService
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


_KST = timezone(timedelta(hours=9))


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
        payment_scheduler_service: PaymentSchedulerService,
        payment_gateway_service: PaymentGatewayService,
        order_query_service: OrderQueryService,
        customer_profile_service: CustomerProfileService,
    ):
        self.uow = uow
        self.seller_store_read_service = seller_store_read_service
        self.seller_product_service = seller_product_service
        self.store_payment_info_service = store_payment_info_service
        self.payment_scheduler_service = payment_scheduler_service
        self.payment_gateway_service = payment_gateway_service
        self.order_query_service = order_query_service
        self.customer_profile_service = customer_profile_service


    async def init_payment(
        self, *, customer_email: str, product_id: str, quantity: int,
    ) -> PaymentInitResponse:
        product = await self.seller_product_service.find_product(product_id)
        if product is None:
            raise ProductNotFoundError("상품을 찾을 수 없습니다")

        await self._assert_pickup_available(product.store_id)

        if product.current_stock < quantity:
            raise StockInsufficientError(
                f"재고가 부족합니다. 현재 재고: {product.current_stock}개",
            )

        # 임시 재고 차감 (낙관적 락 재시도). 실패 시 cleanup 불필요 — 아직 cart/order 생성 전.
        try:
            await self.seller_product_service.consume_purchased_stock(
                product_id=product_id, quantity=quantity,
            )
        except ProductStockInsufficientError:
            raise StockInsufficientError("재고가 부족합니다")
        except ProductStockConflictError:
            raise StockConflictError("재고 차감 중 충돌이 발생했습니다")

        payment_id = generate_payment_id()
        total_amount = _total_amount(price=product.price, sale=product.sale, quantity=quantity)

        # PortOne IDs 조회 — 실패 시 차감된 재고 복구 후 raise.
        try:
            payment_info = await self.store_payment_info_service.get_complete_by_store(
                product.store_id,
            )
        except (PaymentInfoMissingError, PaymentInfoIncompleteError):
            await self._safe_restore_stock(product_id, quantity)
            raise

        await self.payment_scheduler_service.schedule_payment_timeout(
            payment_id=payment_id, product_id=product_id, quantity=quantity,
        )
        await self.order_query_service.create_cart_item(
            payment_id=payment_id,
            product_id=product_id,
            customer_id=customer_email,
            quantity=quantity,
            price=product.price,
            sale=product.sale,
            total_amount=total_amount,
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
        # 1) 스케줄러에서 타임아웃 job 제거. 없으면 이미 타임아웃 (= 5분 경과).
        if not self.payment_scheduler_service.remove_payment_schedule(payment_id):
            raise PaymentTimeoutError("결제 시간이 만료되었습니다.")

        cart_item = await self.order_query_service.get_cart_item(payment_id)
        if cart_item is None:
            raise PaymentNotFoundError("결제 정보를 찾을 수 없습니다")
        if cart_item.customer_id != customer_email:
            raise PaymentOwnershipMismatchError("결제에 대한 권한이 없습니다")

        product = await self.seller_product_service.find_product(cart_item.product_id)
        if product is None:
            raise ProductNotFoundError("상품 정보를 찾을 수 없습니다")

        # portone IDs 확인 + 픽업 시간 검증.
        payment_info = await self.store_payment_info_service.get_by_store(
            product.store_id,
        )
        await self._assert_pickup_available(product.store_id)

        try:
            # 2) PortOne 검증.
            payment_details = await self.payment_gateway_service.verify(
                payment_id=payment_id, secret_key=payment_info.portone_secret_key,
            )
            logger.info(
                "결제 검증 성공 — customer={}, method={}, amount={}",
                cart_item.customer_id,
                payment_details.get("payment_method"),
                payment_details.get("amount"),
            )

            # 3) customer 선호 snapshot + Order 생성 + cart 삭제 — 원자성 위해 한 트랜잭션.
            preference = await self.customer_profile_service.get_preference_snapshot(
                customer_email,
            )
            await self._persist_order_and_clear_cart(
                cart_item=cart_item, preference_snapshot=preference,
            )
        except (PaymentVerificationError, Exception) as e:
            logger.error("결제 확인 중 오류 — 환불 + 재고 복구 시도: {}", e)
            await self._rollback_payment(
                payment_id=payment_id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                secret_key=payment_info.portone_secret_key,
                reason=f"결제 확인 중 오류 발생: {e}",
            )
            raise

        # 4) 예약 완료 이메일은 RDB 트랜잭션과 무관 — background.
        from app.core.email.notifier import send_reservation_email
        background_tasks.add_task(send_reservation_email, customer_email)

        return PaymentResponse(payment_id=payment_id)


    # ───────── private ─────────


    @transactional
    async def _persist_order_and_clear_cart(
        self, *, cart_item, preference_snapshot,
    ) -> None:
        """OrderCurrentItem 생성 + CartItem 삭제 — 한 트랜잭션 안에서 원자적으로.

        `@transactional` 의 ContextVar 메커니즘이 nested `OrderQueryService` @transactional
        호출에 같은 세션을 전달해 부분 commit 위험을 차단한다.
        """
        await self.order_query_service.create_order_from_cart(
            cart_item=cart_item, preference_snapshot=preference_snapshot,
        )
        await self.order_query_service.delete_cart_item(cart_item.payment_id)


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
        try:
            await self.seller_product_service.restore_purchased_stock(
                product_id=product_id, quantity=quantity,
            )
        except Exception as e:
            logger.error("재고 복구 실패 (safe): {}", e)


    async def _rollback_payment(
        self,
        *,
        payment_id: str,
        product_id: str,
        quantity: int,
        secret_key: Optional[str],
        reason: str,
    ) -> None:
        if secret_key:
            try:
                await self.payment_gateway_service.refund(
                    payment_id=payment_id, secret_key=secret_key, reason=reason,
                )
            except PaymentRefundError as e:
                logger.error("롤백 환불 실패: {}", e)
        await self._safe_restore_stock(product_id, quantity)
        try:
            await self.order_query_service.delete_cart_item(payment_id)
        except Exception as e:
            logger.error("롤백 cart 삭제 실패: {}", e)


def _total_amount(*, price: int, sale: Optional[int], quantity: int) -> int:
    """sale 이 있으면 100원 단위 올림, 없으면 그대로 곱."""
    if sale:
        discounted = price * (100 - sale) / 100
        unit = int(((discounted + 99) // 100) * 100)
        return unit * quantity
    return price * quantity
