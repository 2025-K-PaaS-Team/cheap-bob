from typing import List, Optional
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from enum import Enum

from app.domain.seller.model.store_product_info import StoreProductInfo
from app.database.postgresql_repository import BaseRepository


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


    async def get_sale_products(self, store_id: Optional[str] = None) -> List[StoreProductInfo]:
        """세일 중인 상품 조회"""
        filters = {"sale": {"not": None}}
        if store_id:
            filters["store_id"] = store_id
        
        return await self.get_many(
            filters=filters,
            order_by=["-sale", "product_name"]
        )


    async def reset_all_inventories(self) -> int:
        """전체 상품의 일일 판매량/관리자 조정값을 0 으로 일괄 리셋. (스케줄러 호출)

        Returns: 업데이트된 row 수.
        """
        stmt = (
            update(StoreProductInfo)
            .values(
                purchased_quantity=0,
                admin_adjustment=0,
                version=StoreProductInfo.version + 1,
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount


    async def adjust_purchased_stock(self, product_id: str, quantity: int) -> StockUpdateResult:
        """``purchased_quantity`` 를 ``quantity`` 만큼 누적 (delta).

        consume 흐름은 quantity > 0, restore 흐름은 quantity < 0.

        가드:
          - product 가 없거나 (race) 검증 실패 시 INSUFFICIENT_STOCK 반환.
          - consume (quantity > 0): 차감 후 ``current_stock`` 이 음수가 되면 거부.
          - restore (quantity < 0): 누계 차감 ``purchased_quantity + delta`` 가 음수가
            되면 거부 (구매한 양보다 많이 복원하려는 경우).

        검증을 통과하면 낙관적 락으로 update — 실패 시 LOCK_CONFLICT.
        """
        product = await self.get_by_pk(product_id)
        if product is None:
            return StockUpdateResult.INSUFFICIENT_STOCK

        if quantity > 0 and product.current_stock < quantity:
            return StockUpdateResult.INSUFFICIENT_STOCK
        if quantity < 0 and product.purchased_quantity + quantity < 0:
            return StockUpdateResult.INSUFFICIENT_STOCK

        success = await self.update_lock(
            product_id,
            conditions={"version": product.version},
            purchased_quantity=product.purchased_quantity + quantity,
            version=product.version + 1,
        )
        if success:
            return StockUpdateResult.SUCCESS
        return StockUpdateResult.LOCK_CONFLICT


    async def adjust_admin_stock(self, product_id: str, adjustment: int) -> StockUpdateResult:
        """판매자가 재고를 조절할 때 업데이트"""
        product = await self.get_by_pk(product_id)
        
        new_total_stock = product.current_stock + adjustment
        if new_total_stock < 0:
            return StockUpdateResult.INSUFFICIENT_STOCK
        
        success = await self.update_lock(
            product_id,
            conditions={"version": product.version},
            admin_adjustment=product.admin_adjustment + adjustment,
            version=product.version + 1
        )
        
        if success:
            return StockUpdateResult.SUCCESS
        
        return StockUpdateResult.LOCK_CONFLICT


    async def set_stock(self, product_id: str, new_stock: int) -> StockUpdateResult:
        """재고를 특정 값으로 설정 (예약된 재고 업데이트용)"""
        product = await self.get_by_pk(product_id)
        if not product:
            return None
        
        success = await self.update_lock(
            product_id,
            conditions={"version": product.version},
            initial_stock = new_stock,
            version=product.version + 1
        )
        
        if success:
            return StockUpdateResult.SUCCESS
        
        return StockUpdateResult.LOCK_CONFLICT


    async def get_with_nutrition_info(self, product_id: str) -> Optional[StoreProductInfo]:
        """영양 정보와 함께 상품 조회"""
        query = (
            select(StoreProductInfo)
            .where(StoreProductInfo.product_id == product_id)
            .options(selectinload(StoreProductInfo.nutrition_info))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def get_by_store_with_nutrition(self, store_id: str) -> List[StoreProductInfo]:
        """가게의 모든 상품을 영양 정보와 함께 조회"""
        query = (
            select(StoreProductInfo)
            .where(StoreProductInfo.store_id == store_id)
            .options(selectinload(StoreProductInfo.nutrition_info))
            .order_by(StoreProductInfo.product_name)
        )
        result = await self.session.execute(query)
        return result.scalars().unique().all()


    async def count_products_by_store(self, store_id: str) -> int:
        """가게의 상품 개수 조회"""
        query = (
            select(func.count())
            .select_from(StoreProductInfo)
            .where(StoreProductInfo.store_id == store_id)
        )
        result = await self.session.execute(query)
        return result.scalar() or 0
