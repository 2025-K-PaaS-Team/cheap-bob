from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from enum import Enum

from database.models.store_product_info import StoreProductInfo
from repositories.base import BaseRepository


class StockUpdateResult(Enum):
    SUCCESS = "success"
    INSUFFICIENT_STOCK = "insufficient_stock"
    LOCK_CONFLICT = "lock_conflict"


class StoreProductInfoRepository(BaseRepository[StoreProductInfo]):
    """ 가게 상품 정보 """
    def __init__(self, session: AsyncSession):
        super().__init__(StoreProductInfo, session)
    
    async def get_by_product_id(self, product_id: str) -> Optional[StoreProductInfo]:
        """상품 ID로 조회"""
        return await self.get_by_pk(product_id)
    
    async def get_by_store_id(self, store_id: str) -> List[StoreProductInfo]:
        """가게 ID로 상품 목록 조회"""
        return await self.get_many(
            filters={"store_id": store_id},
            order_by=["product_name"]
        )
        
    # async def get_available_products(self, store_id: str) -> List[StoreProductInfo]:
    #     """재고가 있는 상품만 조회"""
    #     return await self.get_many(
    #         filters={
    #             "store_id": store_id,
    #             "current_stock": {"gt": 0}
    #         },
    #         order_by=["-current_stock", "product_name"]
    #     )
    
    async def get_sale_products(self, store_id: Optional[str] = None) -> List[StoreProductInfo]:
        """세일 중인 상품 조회"""
        filters = {"sale": {"not": None}}
        if store_id:
            filters["store_id"] = store_id
        
        return await self.get_many(
            filters=filters,
            order_by=["-sale", "product_name"]
        )
    
    async def decrease_stock(self, product_id: str, quantity: int) -> StockUpdateResult:
        """재고 차감 (낙관적 락 사용)"""
        product = await self.get_by_pk(product_id)
        if not product or product.current_stock < quantity:
            return StockUpdateResult.INSUFFICIENT_STOCK
        
        success = await self.update_lock(
            product_id,
            conditions={"version": product.version},  # 버전 체크
            current_stock=product.current_stock - quantity,
            version=product.version + 1
        )
        
        if success:
            return StockUpdateResult.SUCCESS
        else:
            return StockUpdateResult.LOCK_CONFLICT
    
    async def restore_stock(self, product_id: str, quantity: int) -> StockUpdateResult:
        """재고 복원"""
        product = await self.get_by_pk(product_id)
        
        success = await self.update_lock(
            product_id,
            conditions={"version": product.version},  # 버전 체크
            current_stock=product.current_stock + quantity,
            version=product.version + 1
        )
        
        if success:
            return StockUpdateResult.SUCCESS
        
        return StockUpdateResult.LOCK_CONFLICT