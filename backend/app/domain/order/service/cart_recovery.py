"""서버 재부팅 시 장바구니 임시 재고 복구.

lifespan 에서 container 의 singleton 으로 가져와 1회 호출. seller 의 재고 조정과 order 의
cart 삭제 모두 service 호출로 처리 (strict service-to-service).
"""
from loguru import logger

from app.domain.seller.service.seller_product import SellerProductService
from app.domain.seller.service.exception import ProductStockConflictError
from app.domain.order.service.order_query import OrderQueryService
from app.database.session import UnitOfWork, transactional


class CartRecoveryService:

    def __init__(
        self,
        uow: UnitOfWork,
        seller_product_service: SellerProductService,
        order_query_service: OrderQueryService,
    ):
        self.uow = uow
        self.seller_product_service = seller_product_service
        self.order_query_service = order_query_service


    async def recover_abandoned_carts(self) -> int:
        cart_items = await self._list_all_cart_items()
        if not cart_items:
            logger.info("복구할 장바구니 아이템이 없습니다.")
            return 0

        logger.info("복구 대상 장바구니 아이템 수: {}", len(cart_items))
        recovered = 0
        for cart in cart_items:
            try:
                await self.seller_product_service.restore_purchased_stock(
                    product_id=cart.product_id, quantity=cart.quantity,
                )
            except ProductStockConflictError as e:
                logger.error(
                    "재고 복구 실패 — payment_id={}, product_id={}: {}",
                    cart.payment_id, cart.product_id, e,
                )
                continue

            if await self.order_query_service.delete_cart_item(cart.payment_id):
                recovered += 1

        logger.info("장바구니 재고 복구 완료 — 총 {}개 처리", recovered)
        return recovered


    @transactional
    async def _list_all_cart_items(self):
        from app.domain.order.repository.cart_item import CartItemRepository

        return await CartItemRepository(self._session).get_many(
            load_relations=["product"],
        )
