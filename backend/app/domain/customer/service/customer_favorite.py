from app.domain.seller.service.seller_store_read import SellerStoreReadService
from app.domain.seller.service.exception import StoreNotFoundError
from app.domain.customer.service.exception import (
    FavoriteAlreadyExistsError,
    FavoriteNotFoundError,
)
from app.domain.customer.repository.customer_favorite import CustomerFavoriteRepository
from app.database.session import UnitOfWork, transactional


class CustomerFavoriteService:
    """즐겨찾기 토글. 가게 존재 확인은 seller 도메인 service 에 위임 (strict service-to-service)."""

    def __init__(
        self,
        uow: UnitOfWork,
        seller_store_read_service: SellerStoreReadService,
    ):
        self.uow = uow
        self.seller_store_read_service = seller_store_read_service


    async def add(self, *, customer_email: str, store_id: str) -> None:
        # 가게 존재 확인 — seller 서비스 호출.
        store = await self.seller_store_read_service.get_with_full_info(store_id)
        if store is None:
            raise StoreNotFoundError("가게를 찾을 수 없습니다")
        await self._add_record(customer_email=customer_email, store_id=store_id)


    @transactional
    async def _add_record(self, *, customer_email: str, store_id: str) -> None:
        repo = CustomerFavoriteRepository(self._session)
        if await repo.find_by_customer_and_store(customer_email, store_id):
            raise FavoriteAlreadyExistsError("이미 즐겨찾기에 등록된 가게입니다")
        await repo.save(customer_email, store_id)


    @transactional
    async def remove(self, *, customer_email: str, store_id: str) -> None:
        deleted = await CustomerFavoriteRepository(self._session).delete(
            customer_email, store_id,
        )
        if not deleted:
            raise FavoriteNotFoundError("즐겨찾기에서 찾을 수 없습니다")
