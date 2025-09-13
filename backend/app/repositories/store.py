from typing import List, Optional, Dict
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.store import Store
from database.models.address import Address
from repositories.base import BaseRepository


class StoreRepository(BaseRepository[Store]):
    """가게"""
    def __init__(self, session: AsyncSession):
        super().__init__(Store, session)
    
    async def get_by_store_id(self, store_id: str) -> Optional[Store]:
        """가게 ID로 조회"""
        return await self.get_by_pk(store_id)
    
    async def get_by_seller_email(self, seller_email: str) -> List[Store]:
        """판매자 이메일로 가게 목록 조회"""
        return await self.get_many(
            filters={"seller_email": seller_email},
            order_by=["-created_at"]
        )
    
    async def get_all_with_relations(self) -> List[Store]:
        """모든 가게를 관계 데이터와 함께 조회"""
        return await self.get_many(
            order_by=["-created_at"],
            load_relations=["seller", "address", "payment_info", "products"]
        )
    
    async def search_by_name(self, keyword: str) -> List[Store]:
        """가게 이름으로 검색"""
        return await self.get_many(
            filters={"store_name": {"like": keyword}},
            order_by=["store_name"]
        )
    
    async def get_with_address(self, store_id: str) -> Optional[Store]:
        """가게를 주소 정보와 함께 조회"""
        query = (
            select(Store)
            .options(selectinload(Store.address))
            .where(Store.store_id == store_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_address_id(self, address_id: int) -> List[Store]:
        """주소 ID로 가게 목록 조회"""
        return await self.get_many(
            filters={"address_id": address_id},
            order_by=["store_name"],
            load_relations=["address"]
        )
    
    async def get_by_area(
        self, 
        sido: Optional[str] = None,
        sigungu: Optional[str] = None,
        bname: Optional[str] = None
    ) -> List[Store]:
        """지역별 가게 조회"""
        query = (
            select(Store)
            .join(Address, Store.address_id == Address.address_id)
            .options(selectinload(Store.address))
        )
        
        conditions = []
        if sido:
            conditions.append(Address.sido == sido)
        if sigungu:
            conditions.append(Address.sigungu == sigungu)
        if bname:
            conditions.append(Address.bname == bname)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(Store.store_name)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update_address(self, store_id: str, address_id: int) -> Optional[Store]:
        """가게의 주소 정보 업데이트"""
        return await self.update(store_id, address_id=address_id)
    
    async def update_store_info(
        self, 
        store_id: str,
        store_introduction: Optional[str] = None,
        store_phone: Optional[str] = None,
        store_postal_code: Optional[str] = None,
        store_address: Optional[str] = None,
        store_detail_address: Optional[str] = None,
        address_id: Optional[int] = None
    ) -> Optional[Store]:
        """가게 정보 업데이트"""
        update_data = {}
        
        if store_introduction is not None:
            update_data["store_introduction"] = store_introduction
        if store_phone is not None:
            update_data["store_phone"] = store_phone
        if store_postal_code is not None:
            update_data["store_postal_code"] = store_postal_code
        if store_address is not None:
            update_data["store_address"] = store_address
        if store_detail_address is not None:
            update_data["store_detail_address"] = store_detail_address
        if address_id is not None:
            update_data["address_id"] = address_id
        
        if update_data:
            return await self.update(store_id, **update_data)
        return await self.get_by_store_id(store_id)