from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from database.models.product_nutrition import ProductNutrition
from database.models.store_product_info import StoreProductInfo
from schemas.food_preferences import NutritionType
from repositories.base import BaseRepository
from database.models.store import Store


class ProductNutritionRepository(BaseRepository[ProductNutrition]):
    """상품 영양 정보 Repository"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(ProductNutrition, session)
    
    async def get_nutrition_types_by_product(self, product_id: str) -> List[NutritionType]:
        """상품의 영양 타입 목록 조회"""
        nutrition_infos = await self.get_by_product_id(product_id)
        return [info.nutrition_type for info in nutrition_infos]
    
    async def get_stores_by_nutrition_types(
        self, 
        nutrition_types: List[NutritionType]
    ) -> List[Store]:
        """여러 영양 타입으로 가게 조회"""
        
        query = (
            select(Store)
            .join(StoreProductInfo, Store.store_id == StoreProductInfo.store_id)
            .join(ProductNutrition, StoreProductInfo.product_id == ProductNutrition.product_id)
            .where(ProductNutrition.nutrition_type.in_(nutrition_types))
            .distinct()
        )
        
        result = await self.session.execute(query)
        return result.scalars().unique().all()
    
    async def add_nutrition_to_product(
        self,
        product_id: str,
        nutrition_type: NutritionType
    ) -> Optional[ProductNutrition]:
        """상품에 영양 정보 추가"""
        # 중복 확인
        existing = await self.get_one(
            product_id=product_id,
            nutrition_type=nutrition_type
        )
        if existing:
            return existing
        
        return await self.create(
            product_id=product_id,
            nutrition_type=nutrition_type
        )
    
    async def add_multiple_nutrition_to_product(
        self,
        product_id: str,
        nutrition_types: List[NutritionType]
    ) -> List[ProductNutrition]:
        """상품에 여러 영양 정보 추가"""
        added_nutrition = []
        
        for nutrition_type in nutrition_types:
            # 중복 확인
            existing = await self.get_one(
                product_id=product_id,
                nutrition_type=nutrition_type
            )
            
            if not existing:
                # 중복이 아닌 경우만 추가
                nutrition_info = await self.create(
                    product_id=product_id,
                    nutrition_type=nutrition_type
                )
                added_nutrition.append(nutrition_info)
            else:
                added_nutrition.append(existing)
        
        # 한 번에 플러시
        await self.session.flush()
        
        # 생성된 정보들 새로고침
        for info in added_nutrition:
            await self.session.refresh(info)
        
        return added_nutrition
    
    async def remove_nutrition_from_product(
        self,
        product_id: str,
        nutrition_type: NutritionType
    ) -> bool:
        """상품에서 영양 정보 제거"""
        query = delete(ProductNutrition).where(
            ProductNutrition.product_id == product_id,
            ProductNutrition.nutrition_type == nutrition_type
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount > 0