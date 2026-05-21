from app.domain.seller.repository.store_product_info import (
    StoreProductInfoRepository,
)
from app.domain.seller.repository.store import StoreRepository
from app.database.session import UnitOfWork, transactional


class SellerRegistrationStatusService:
    """판매자의 온보딩 진행 상태 ("store" | "product" | "complete").

    auth 의 `RegistrationStatusService` 가 seller 분기에서 본 서비스를 호출한다.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    @transactional
    async def get_status(self, seller_email: str) -> str:
        stores = await StoreRepository(self._session).get_by_seller_email(seller_email)
        if not stores:
            return "store"

        product_count = await StoreProductInfoRepository(
            self._session,
        ).count_products_by_store(stores[0].store_id)
        return "complete" if product_count > 0 else "product"
