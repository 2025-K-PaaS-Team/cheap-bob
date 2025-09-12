from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from repositories.base import BaseRepository
from database.models.customer_preferences import CustomerPreferredMenu, CustomerNutritionType, CustomerAllergy
from schemas.food_preferences import PreferredMenu, NutritionType, AllergyType


class CustomerPreferredMenuRepository(BaseRepository[CustomerPreferredMenu]):
    def __init__(self, session: AsyncSession):
        super().__init__(CustomerPreferredMenu, session)
    
    async def get_by_customer(self, customer_email: str) -> List[CustomerPreferredMenu]:
        """특정 고객의 모든 선호 메뉴 조회"""
        result = await self.session.execute(
            select(self.model).where(self.model.customer_email == customer_email)
        )
        return result.scalars().all()
    
    async def create_for_customer(self, customer_email: str, menu_type: PreferredMenu) -> CustomerPreferredMenu:
        """고객의 선호 메뉴 추가"""
        return await self.create(
            customer_email=customer_email,
            menu_type=menu_type
        )
    
    async def create_bulk_for_customer(self, customer_email: str, menu_types: List[PreferredMenu]) -> List[CustomerPreferredMenu]:
        """고객의 여러 선호 메뉴 한번에 추가"""
        created_items = []
        for menu_type in menu_types:
            obj = self.model(
                customer_email=customer_email,
                menu_type=menu_type
            )
            self.session.add(obj)
            created_items.append(obj)
        
        await self.session.commit()
        for obj in created_items:
            await self.session.refresh(obj)
        return created_items
    
    async def delete_for_customer(self, customer_email: str, menu_type: PreferredMenu) -> bool:
        """고객의 특정 선호 메뉴 삭제"""
        result = await self.session.execute(
            delete(self.model).where(
                self.model.customer_email == customer_email,
                self.model.menu_type == menu_type
            )
        )
        await self.session.commit()
        return result.rowcount > 0


class CustomerNutritionTypeRepository(BaseRepository[CustomerNutritionType]):
    def __init__(self, session: AsyncSession):
        super().__init__(CustomerNutritionType, session)
    
    async def get_by_customer(self, customer_email: str) -> List[CustomerNutritionType]:
        """특정 고객의 모든 영양 타입 조회"""
        result = await self.session.execute(
            select(self.model).where(self.model.customer_email == customer_email)
        )
        return result.scalars().all()
    
    async def create_for_customer(self, customer_email: str, nutrition_type: NutritionType) -> CustomerNutritionType:
        """고객의 영양 타입 추가"""
        return await self.create(
            customer_email=customer_email,
            nutrition_type=nutrition_type
        )
    
    async def create_bulk_for_customer(self, customer_email: str, nutrition_types: List[NutritionType]) -> List[CustomerNutritionType]:
        """고객의 여러 영양 타입 한번에 추가"""
        created_items = []
        for nutrition_type in nutrition_types:
            obj = self.model(
                customer_email=customer_email,
                nutrition_type=nutrition_type
            )
            self.session.add(obj)
            created_items.append(obj)
        
        await self.session.commit()
        for obj in created_items:
            await self.session.refresh(obj)
        return created_items
    
    async def delete_for_customer(self, customer_email: str, nutrition_type: NutritionType) -> bool:
        """고객의 특정 영양 타입 삭제"""
        result = await self.session.execute(
            delete(self.model).where(
                self.model.customer_email == customer_email,
                self.model.nutrition_type == nutrition_type
            )
        )
        await self.session.commit()
        return result.rowcount > 0


class CustomerAllergyRepository(BaseRepository[CustomerAllergy]):
    def __init__(self, session: AsyncSession):
        super().__init__(CustomerAllergy, session)
    
    async def get_by_customer(self, customer_email: str) -> List[CustomerAllergy]:
        """특정 고객의 모든 알레르기 조회"""
        result = await self.session.execute(
            select(self.model).where(self.model.customer_email == customer_email)
        )
        return result.scalars().all()
    
    async def create_for_customer(self, customer_email: str, allergy_type: AllergyType) -> CustomerAllergy:
        """고객의 알레르기 추가"""
        return await self.create(
            customer_email=customer_email,
            allergy_type=allergy_type
        )
    
    async def create_bulk_for_customer(self, customer_email: str, allergy_types: List[AllergyType]) -> List[CustomerAllergy]:
        """고객의 여러 알레르기 한번에 추가"""
        created_items = []
        for allergy_type in allergy_types:
            obj = self.model(
                customer_email=customer_email,
                allergy_type=allergy_type
            )
            self.session.add(obj)
            created_items.append(obj)
        
        await self.session.commit()
        for obj in created_items:
            await self.session.refresh(obj)
        return created_items
    
    async def delete_for_customer(self, customer_email: str, allergy_type: AllergyType) -> bool:
        """고객의 특정 알레르기 삭제"""
        result = await self.session.execute(
            delete(self.model).where(
                self.model.customer_email == customer_email,
                self.model.allergy_type == allergy_type
            )
        )
        await self.session.commit()
        return result.rowcount > 0