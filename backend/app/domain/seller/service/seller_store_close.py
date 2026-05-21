"""/seller/store/close — 가게 마감 + 진행중 주문 환불.

OrderQueryService / SellerProductService / PaymentGatewayService / StorePaymentInfoService 협력.
"""
from typing import Tuple

from app.domain.seller.service.seller_product import SellerProductService
from app.domain.seller.service.exception import (
    StoreNotFoundError,
    StorePaymentMissingError,
)
from app.domain.seller.repository.store_operation_info import (
    StoreOperationInfoRepository,
)
from app.domain.payment.service.store_payment_info import StorePaymentInfoService
from app.domain.payment.service.payment_gateway import PaymentGatewayService
from app.domain.payment.service.exception import (
    PaymentInfoIncompleteError,
    PaymentInfoMissingError,
)
from app.domain.order.service.order_query import OrderQueryService
from app.domain.order.dto.order import OrderStatus
from app.database.session import UnitOfWork, transactional
from app.core.logger import get_logger


logger = get_logger("seller.service.seller_store_close")


class SellerStoreCloseService:
    """가게 마감 + 진행중 주문 자동 환불 — order/payment 협력."""

    def __init__(
        self,
        uow: UnitOfWork,
        order_query_service: OrderQueryService,
        seller_product_service: SellerProductService,
        payment_gateway_service: PaymentGatewayService,
        store_payment_info_service: StorePaymentInfoService,
    ):
        self.uow = uow
        self.order_query_service = order_query_service
        self.seller_product_service = seller_product_service
        self.payment_gateway_service = payment_gateway_service
        self.store_payment_info_service = store_payment_info_service


    async def close(self, store_id: str) -> Tuple[int, str]:
        """가게 마감 처리. 환불된 주문 건수와 안내 메시지 반환."""
        await self._set_today_closed(store_id)

        try:
            payment_info = await self.store_payment_info_service.get_complete_by_store(
                store_id,
            )
        except (PaymentInfoMissingError, PaymentInfoIncompleteError) as e:
            raise StorePaymentMissingError(str(e))

        current_orders = await self.order_query_service.list_store_current_orders(
            store_id,
        )

        refund_count = 0
        active = {OrderStatus.reservation, OrderStatus.accept}
        for order in current_orders:
            if order.status not in active:
                continue
            try:
                await self.payment_gateway_service.refund(
                    payment_id=order.payment_id,
                    secret_key=payment_info.portone_secret_key,
                    reason="‘기타 사정’ 으로 주문이 취소되었어요.",
                )
                quantity = await self.order_query_service.cancel_order(
                    payment_id=order.payment_id,
                    cancel_reason="‘기타 사정’ 으로 주문이 취소되었어요.",
                )
                await self.seller_product_service.restore_purchased_stock(
                    product_id=order.product_id, quantity=quantity,
                )
                refund_count += 1
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
