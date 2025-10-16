from typing import Optional
from datetime import datetime

from database.mongodb_models.customer_withdraw_reservation import CustomerWithdrawReservation
from repositories.mongodb_base import BaseMongoRepository


class CustomerWithdrawReservationRepository(BaseMongoRepository[CustomerWithdrawReservation]):
    """소비자 탈퇴 예약 Repository"""
    
    def __init__(self):
        super().__init__(CustomerWithdrawReservation)
    
    async def create_withdrawal(self, customer_email: str, withdrawn_at: datetime) -> CustomerWithdrawReservation:
        """소비자 탈퇴 기록 생성"""
        withdrawal = CustomerWithdrawReservation(
            customer_email=customer_email,
            withdrawn_at=withdrawn_at
        )
        return await self.create(withdrawal)
    
    async def get_by_customer_email(self, customer_email: str) -> Optional[CustomerWithdrawReservation]:
        """소비자 이메일로 탈퇴 기록 조회"""
        return await self.get_one(customer_email=customer_email)
    
    async def delete_by_customer_email(self, customer_email: str) -> bool:
        """소비자 이메일로 탈퇴 기록 삭제"""
        withdrawal = await self.get_by_customer_email(customer_email)
        if withdrawal:
            return await self.delete(withdrawal)
        return False
    
    async def exists_by_customer_email(self, customer_email: str) -> bool:
        """소비자 이메일로 탈퇴 기록 존재 여부 확인"""
        return await self.exists(customer_email=customer_email)