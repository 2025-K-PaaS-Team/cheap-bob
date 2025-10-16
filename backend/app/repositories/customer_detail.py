from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.base import BaseRepository
from database.models.customer_detail import CustomerDetail


class CustomerDetailRepository(BaseRepository[CustomerDetail]):
    def __init__(self, session: AsyncSession):
        super().__init__(CustomerDetail, session)
    
    async def get_by_customer(self, customer_email: str) -> Optional[CustomerDetail]:
        """소비자 이메일로 상세 정보 조회"""
        return await self.get_by_pk(customer_email)
    
    async def create_for_customer(
        self, 
        customer_email: str, 
        nickname: str, 
        phone_number: str
    ) -> CustomerDetail:
        """소비자 상세 정보 생성"""
        return await self.create(
            customer_email=customer_email,
            nickname=nickname,
            phone_number=phone_number
        )
    
    async def update_for_customer(
        self, 
        customer_email: str,
        **kwargs
    ) -> Optional[CustomerDetail]:
        """소비자 상세 정보 업데이트"""
        return await self.update(customer_email, **kwargs)
    
    async def update_nickname(
        self,
        customer_email: str,
        nickname: str
    ) -> Optional[CustomerDetail]:
        """닉네임만 업데이트"""
        return await self.update(customer_email, nickname=nickname)
    
    async def update_phone_number(
        self,
        customer_email: str,
        phone_number: str
    ) -> Optional[CustomerDetail]:
        """전화번호만 업데이트"""
        return await self.update(customer_email, phone_number=phone_number)
    
    async def exists_for_customer(self, customer_email: str) -> bool:
        """소비자 상세 정보 존재 여부 확인"""
        return await self.exists(customer_email=customer_email)
    
    async def delete_for_customer(self, customer_email: str) -> bool:
        """소비자 상세 정보 삭제"""
        return await self.delete(customer_email)