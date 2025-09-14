from typing import Optional, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models.store_sns import StoreSNS
from database.models.store import Store
from repositories.base import BaseRepository


class StoreSNSRepository(BaseRepository[StoreSNS]):
    """가게 SNS 정보 Repository"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(StoreSNS, session)
    
    async def get_by_store_id(self, store_id: str) -> Optional[StoreSNS]:
        """가게 ID로 SNS 정보 조회"""
        return await self.get_one(store_id=store_id)
    
    async def create_or_update(
        self,
        store_id: str,
        instagram: Optional[str] = None,
        facebook: Optional[str] = None,
        x: Optional[str] = None,
        homepage: Optional[str] = None
    ) -> StoreSNS:
        """SNS 정보 생성 또는 업데이트"""
        existing = await self.get_by_store_id(store_id)
        
        if existing:
            # 업데이트
            update_data = {}
            if instagram is not None:
                update_data["instagram"] = instagram
            if facebook is not None:
                update_data["facebook"] = facebook
            if x is not None:
                update_data["x"] = x
            if homepage is not None:
                update_data["homepage"] = homepage
            
            if update_data:
                return await self.update(existing.sns_id, **update_data)
            return existing
        else:
            # 생성
            return await self.create(
                store_id=store_id,
                instagram=instagram,
                facebook=facebook,
                x=x,
                homepage=homepage
            )
    
    async def update_sns_info(
        self,
        store_id: str,
        sns_data: Dict[str, Optional[str]]
    ) -> Optional[StoreSNS]:
        """SNS 정보 일괄 업데이트"""
        existing = await self.get_by_store_id(store_id)
        if not existing:
            return None
        
        update_data = {}
        for platform in ["instagram", "facebook", "x", "homepage"]:
            if platform in sns_data:
                update_data[platform] = sns_data[platform]
        
        if update_data:
            return await self.update(existing.sns_id, **update_data)
        return existing

    async def delete_by_store_id(self, store_id: str) -> bool:
        """가게 ID로 SNS 정보 삭제"""
        sns_info = await self.get_by_store_id(store_id)
        if sns_info:
            return await self.delete(sns_info.sns_id)
        return False