from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.payment.model.store_payment_info import StorePaymentInfo
from app.database.postgresql_repository import BaseRepository


class StorePaymentInfoRepository(BaseRepository[StorePaymentInfo]):
    """가게 결제 정보"""
    def __init__(self, session: AsyncSession):
        super().__init__(StorePaymentInfo, session)


    async def get_by_store_id(self, store_id: str) -> Optional[StorePaymentInfo]:
        """가게 ID로 결제 정보 조회"""
        return await self.get_by_pk(store_id)


    async def exists_by_store_id(self, store_id: str) -> bool:
        """가게의 결제 정보 존재 여부 확인"""
        return await self.exists(store_id=store_id)


    async def update_portone_info(
        self,
        store_id: str,
        portone_store_id: str,
        portone_channel_id: str,
    ) -> Optional[StorePaymentInfo]:
        """포트원 ID 갱신. 대상이 없으면 None."""
        return await self.update(
            store_id,
            portone_store_id=portone_store_id,
            portone_channel_id=portone_channel_id,
        )


    async def update_secret_key(
        self, store_id: str, portone_secret_key: str,
    ) -> Optional[StorePaymentInfo]:
        """secret key 단독 갱신 — rotate 시 사용."""
        return await self.update(
            store_id, portone_secret_key=portone_secret_key,
        )


    async def has_complete_info(self, store_id: str) -> bool:
        """결제 정보가 완전한지 확인"""
        payment_info = await self.get_by_pk(store_id)
        if not payment_info:
            return False
        
        return all([
            payment_info.portone_store_id,
            payment_info.portone_channel_id,
            payment_info.portone_secret_key
        ])