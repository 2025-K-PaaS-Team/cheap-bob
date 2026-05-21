from app.domain.seller.service.exception import StoreNotFoundError
from app.domain.seller.repository.store import StoreRepository
from app.domain.seller.model.store import Store
from app.database.session import UnitOfWork, transactional


class SellerStoreProfileService:
    """가게 기본 정보 (이름/소개/전화) 업데이트."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    @transactional
    async def _update_field(self, store_id: str, **kwargs) -> Store:
        repo = StoreRepository(self._session)
        store = await repo.update(store_id, **kwargs)
        if store is None:
            raise StoreNotFoundError("가게를 찾을 수 없습니다.")
        return store


    async def update_name(self, store_id: str, store_name: str) -> Store:
        return await self._update_field(store_id, store_name=store_name)


    async def update_introduction(self, store_id: str, store_introduction: str) -> Store:
        return await self._update_field(
            store_id, store_introduction=store_introduction,
        )


    async def update_phone(self, store_id: str, store_phone: str) -> Store:
        return await self._update_field(store_id, store_phone=store_phone)
