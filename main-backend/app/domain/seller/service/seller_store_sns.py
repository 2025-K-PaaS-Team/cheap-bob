from typing import Optional

from app.domain.seller.service.exception import StoreSNSNotFoundError
from app.domain.seller.repository.store_sns import StoreSNSRepository
from app.domain.seller.model.store_sns import StoreSNS
from app.database.session import UnitOfWork, transactional


class SellerStoreSNSService:
    """가게 SNS CRUD."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    @transactional
    async def get(self, store_id: str) -> Optional[StoreSNS]:
        return await StoreSNSRepository(self._session).get_by_store_id(store_id)


    @transactional
    async def update(
        self,
        *,
        store_id: str,
        instagram: Optional[str] = None,
        facebook: Optional[str] = None,
        x: Optional[str] = None,
        homepage: Optional[str] = None,
    ) -> StoreSNS:
        """전달된 필드만 갱신. 한 필드도 없는 경우 현재 값 그대로 반환."""
        repo = StoreSNSRepository(self._session)
        updated = await repo.update_and_return(
            store_id=store_id,
            instagram=instagram,
            facebook=facebook,
            x=x,
            homepage=homepage,
        )
        if updated is None:
            raise StoreSNSNotFoundError("등록된 SNS 정보를 찾을 수 없습니다.")
        return updated


    async def delete_field(self, store_id: str, sns_type: str) -> None:
        """sns_type ∈ {instagram, facebook, x, homepage}. 해당 필드를 NULL 로."""
        await self.update(store_id=store_id, **{sns_type: None})
