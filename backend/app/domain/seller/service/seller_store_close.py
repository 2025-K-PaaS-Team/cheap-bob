"""/seller/store/close — 가게 마감 + 진행중 주문 환불.

payment 도메인 분리 후 환불은 payment-svc internal API 한 번에 위임.
"""
from typing import Tuple

from app.domain.seller.service.seller_product import SellerProductService
from app.domain.seller.service.exception import StorePaymentMissingError
from app.domain.seller.repository.store_operation_info import (
    StoreOperationInfoRepository,
)
from app.domain.order.service.order_query import OrderQueryService
from app.domain.order.dto.order import OrderStatus
from app.database.session import UnitOfWork, transactional
from app.core.logger import get_logger
from app.core.internal_client.payment import (
    InternalPaymentClient,
    PaymentServiceError,
    PaymentServiceUnavailableError,
)


logger = get_logger("seller.service.seller_store_close")


class SellerStoreCloseService:
    """가게 마감 + 진행중 주문 자동 환불 — payment-svc 위임."""

    def __init__(
        self,
        uow: UnitOfWork,
        order_query_service: OrderQueryService,
        seller_product_service: SellerProductService,
        internal_payment_client: InternalPaymentClient,
    ):
        self.uow = uow
        self.order_query_service = order_query_service
        self.seller_product_service = seller_product_service
        self.internal_payment_client = internal_payment_client


    async def close(self, store_id: str) -> Tuple[int, str]:
        await self._set_today_closed(store_id)

        # 사전 — 결제 설정이 없으면 사용자에게 명시적 에러.
        try:
            has = await self.internal_payment_client.has_complete_info(store_id)
        except PaymentServiceUnavailableError as e:
            raise StorePaymentMissingError(f"payment-svc 일시 장애: {e.detail}")
        if not has:
            raise StorePaymentMissingError("가게의 결제 설정이 완료되지 않았습니다")

        current_orders = await self.order_query_service.list_store_current_orders(
            store_id,
        )

        refund_count = 0
        active = {OrderStatus.reservation, OrderStatus.accept}
        reason = "‘기타 사정’ 으로 주문이 취소되었어요."
        for order in current_orders:
            if order.status not in active:
                continue
            try:
                await self.internal_payment_client.refund(
                    payment_id=order.payment_id,
                    store_id=store_id,
                    reason=reason,
                )
                quantity = await self.order_query_service.cancel_order(
                    payment_id=order.payment_id, cancel_reason=reason,
                )
                await self.seller_product_service.restore_purchased_stock(
                    product_id=order.product_id, quantity=quantity,
                )
                refund_count += 1
            except (PaymentServiceError, PaymentServiceUnavailableError) as e:
                logger.error("마감 환불 처리 중 payment-svc 오류 payment_id={}: {}",
                             order.payment_id, e)
            except Exception as e:
                logger.error("마감 환불 처리 중 오류: {}", e)

        return refund_count, "가게가 마감되었습니다"


    @transactional
    async def _set_today_closed(self, store_id: str) -> None:
        operation_repo = StoreOperationInfoRepository(self._session)
        today_op = await operation_repo.get_today_operation_info(store_id)
        if today_op:
            await operation_repo.update_open_status(
                operation_id=today_op.operation_id, is_currently_open=False,
            )
