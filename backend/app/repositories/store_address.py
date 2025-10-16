from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.store_address import StoreAddress
from repositories.base import BaseRepository


class StoreAddressRepository(BaseRepository[StoreAddress]):
    """주소 정보 Repository"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(StoreAddress, session)
    
    async def get_by_address_id(self, address_id: int) -> Optional[StoreAddress]:
        """주소 ID로 조회"""
        return await self.get_by_pk(address_id)
    
    async def find_by_full_address(self, sido: str, sigungu: str, bname: str) -> Optional[StoreAddress]:
        """전체 주소 정보로 조회"""
        return await self.get_one(
            sido=sido,
            sigungu=sigungu,
            bname=bname
        )
    
    async def get_by_sido(self, sido: str) -> List[StoreAddress]:
        """시/도로 검색"""
        return await self.get_many(
            filters={"sido": sido},
            order_by=["sigungu", "bname"]
        )
    
    async def get_by_sigungu(self, sido: str, sigungu: str) -> List[StoreAddress]:
        """시/도와 시/군/구로 검색"""
        return await self.get_many(
            filters={
                "sido": sido,
                "sigungu": sigungu
            },
            order_by=["bname"]
        )
    
    async def get_address_hierarchy(self) -> Dict[str, Dict[str, List[str]]]:
        """전체 주소 계층 구조 조회"""
        addresses = await self.get_many(order_by=["sido", "sigungu", "bname"])
        
        hierarchy = {}
        for addr in addresses:
            if addr.sido not in hierarchy:
                hierarchy[addr.sido] = {}
            if addr.sigungu not in hierarchy[addr.sido]:
                hierarchy[addr.sido][addr.sigungu] = []
            if addr.bname not in hierarchy[addr.sido][addr.sigungu]:
                hierarchy[addr.sido][addr.sigungu].append(addr.bname)
        
        return hierarchy
    
    async def create_with_coordinates(self, sido: str, sigungu: str, bname: str, lat: str, lng: str) -> StoreAddress:
        """위도/경도 정보를 포함한 주소 생성"""
        return await self.create(
            sido=sido,
            sigungu=sigungu,
            bname=bname,
            lat=lat,
            lng=lng
        )
    
    async def update_address_with_coordinates(self, address_id: int, 
                                             sido: str, sigungu: str, bname: str,
                                             lat: str, lng: str) -> StoreAddress:
        """주소 전체 정보와 위도/경도 업데이트"""
        return await self.update(
            address_id,
            sido=sido,
            sigungu=sigungu,
            bname=bname,
            lat=lat,
            lng=lng
        )