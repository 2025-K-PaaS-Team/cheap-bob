from typing import List, Optional, Tuple, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from enum import Enum

from database.models.store_product_info import StoreProductInfo
from database.models.product_nutrition import ProductNutrition
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
    
    async def get_sale_products(self, store_id: Optional[str] = None) -> List[StoreProductInfo]:
        """세일 중인 상품 조회"""
        filters = {"sale": {"not": None}}
        if store_id:
            filters["store_id"] = store_id
        
        return await self.get_many(
            filters=filters,
            order_by=["-sale", "product_name"]
        )
    
    async def adjust_purchased_stock(self, product_id: str, quantity: int) -> StockUpdateResult:
        """소비자가 상품을 사고/환불 할 때 업데이트"""
        product = await self.get_by_pk(product_id)
        if quantity < 0 and product.current_stock < quantity:
            return StockUpdateResult.INSUFFICIENT_STOCK
        
        success = await self.update_lock(
            product_id,
            conditions={"version": product.version},
            purchased_quantity=product.purchased_quantity + quantity,
            version=product.version + 1
        )
        
        if success:
            return StockUpdateResult.SUCCESS
        else:
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
    
    async def create_product_with_nutrition(
        self,
        product_id: str,
        store_id: str,
        product_name: str,
        description: str,
        initial_stock: int,
        price: int,
        sale: Optional[int] = None,
        nutrition_types: Optional[List[str]] = None
    ) -> Tuple[StoreProductInfo, List[str]]:
        """상품과 영양 정보를 한 번에 생성"""
        try:
            # 1. 상품 생성
            product = StoreProductInfo(
                product_id=product_id,
                store_id=store_id,
                product_name=product_name,
                description=description,
                initial_stock=initial_stock,
                purchased_quantity=0,  # 초기값 0
                admin_adjustment=0,    # 초기값 0
                price=price,
                sale=sale,
                version=1
            )
            self.session.add(product)
            
            # 2. 영양 정보 생성
            created_nutrition_types = []
            if nutrition_types:
                for nutrition_type in nutrition_types:
                    nutrition = ProductNutrition(
                        product_id=product_id,
                        nutrition_type=nutrition_type
                    )
                    self.session.add(nutrition)
                    created_nutrition_types.append(nutrition_type)
            
            # 3. 모든 변경사항 커밋
            await self.session.flush()
            
            # 4. 상품 객체 새로고침 (영양 정보 포함)
            await self.session.refresh(product, ["nutrition_info"])
            
            return product, created_nutrition_types
            
        except Exception as e:
            # 트랜잭션 롤백은 상위에서 처리
            raise e