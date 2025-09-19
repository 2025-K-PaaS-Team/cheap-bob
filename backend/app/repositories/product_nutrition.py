from typing import List, Optional, Dict, Tuple
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
    
    async def get_by_product_id(self, product_id: str) -> List[ProductNutrition]:
        """상품 ID로 영양 정보 목록 조회"""
        return await self.get_many(filters={"product_id": product_id})
    
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
    
    async def get_nutrition_types_by_products(
        self, 
        product_ids: List[str]
    ) -> Dict[str, List[NutritionType]]:
        """여러 상품의 영양 타입을 한 번에 조회"""
        if not product_ids:
            return {}
        
        query = (
            select(ProductNutrition)
            .where(ProductNutrition.product_id.in_(product_ids))
        )
        
        result = await self.session.execute(query)
        nutrition_infos = result.scalars().all()
        
        # 상품 ID별로 그룹화
        nutrition_by_product: Dict[str, List[NutritionType]] = {}
        for info in nutrition_infos:
            if info.product_id not in nutrition_by_product:
                nutrition_by_product[info.product_id] = []
            nutrition_by_product[info.product_id].append(info.nutrition_type)
        
        # 영양 정보가 없는 상품은 빈 리스트로 설정
        for product_id in product_ids:
            if product_id not in nutrition_by_product:
                nutrition_by_product[product_id] = []
        
        return nutrition_by_product
    
    async def add_nutrition_with_validation(
        self,
        product_id: str,
        nutrition_types: List[NutritionType]
    ) -> Tuple[List[NutritionType], List[NutritionType]]:
        """영양 정보 추가 (중복 체크 포함, DB 호출 1번)
        
        Returns:
            Tuple[업데이트된 전체 영양 타입 리스트, 중복된 영양 타입 리스트]
        """
        try:
            # 1. 기존 영양 정보 조회
            query = (
                select(ProductNutrition)
                .where(ProductNutrition.product_id == product_id)
            )
            result = await self.session.execute(query)
            existing_nutritions = result.scalars().all()
            
            # 기존 영양 타입 집합
            existing_types = {n.nutrition_type for n in existing_nutritions}
            
            # 2. 중복 체크
            duplicates = [nt for nt in nutrition_types if nt in existing_types]
            
            # 중복이 있으면 즉시 반환 (DB 변경 없이)
            if duplicates:
                return list(existing_types), duplicates
            
            # 3. 새로운 영양 정보 추가
            new_nutritions = []
            for nutrition_type in nutrition_types:
                if nutrition_type not in existing_types:
                    nutrition = ProductNutrition(
                        product_id=product_id,
                        nutrition_type=nutrition_type
                    )
                    self.session.add(nutrition)
                    new_nutritions.append(nutrition)
            
            # 4. 변경사항 플러시
            if new_nutritions:
                await self.session.flush()
                
                # 새로 추가된 정보들 새로고침
                for nutrition in new_nutritions:
                    await self.session.refresh(nutrition)
            
            # 5. 업데이트된 전체 영양 타입 리스트 반환
            all_nutrition_types = list(existing_types) + [n.nutrition_type for n in new_nutritions]
            
            return all_nutrition_types, []
            
        except Exception as e:
            # 트랜잭션 롤백은 상위에서 처리
            raise e