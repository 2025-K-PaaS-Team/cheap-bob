from typing import List, Optional, Dict
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.address import Address
from repositories.base import BaseRepository


class AddressRepository(BaseRepository[Address]):
    """주소 정보 Repository"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Address, session)
    
    async def get_by_address_id(self, address_id: int) -> Optional[Address]:
        """주소 ID로 조회"""
        return await self.get_by_pk(address_id)
    
    async def find_by_full_address(self, sido: str, sigungu: str, bname: str) -> Optional[Address]:
        """전체 주소 정보로 조회"""
        return await self.get_one(
            sido=sido,
            sigungu=sigungu,
            bname=bname
        )
    
    async def get_by_sido(self, sido: str) -> List[Address]:
        """시/도로 검색"""
        return await self.get_many(
            filters={"sido": sido},
            order_by=["sigungu", "bname"]
        )
    
    async def get_by_sigungu(self, sido: str, sigungu: str) -> List[Address]:
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