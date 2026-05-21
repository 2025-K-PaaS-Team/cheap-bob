from typing import Optional
from datetime import datetime

from app.domain.seller.model.seller_withdraw_reservation import SellerWithdrawReservation
from app.database.mongodb_repository import BaseMongoRepository


class SellerWithdrawReservationRepository(BaseMongoRepository[SellerWithdrawReservation]):
    """판매자 탈퇴 예약 Repository"""
    
    def __init__(self):
        super().__init__(SellerWithdrawReservation)


    async def create_withdrawal(self, seller_email: str, withdrawn_at: datetime) -> SellerWithdrawReservation:
        """판매자 탈퇴 기록 생성"""
        withdrawal = SellerWithdrawReservation(
            seller_email=seller_email,
            withdrawn_at=withdrawn_at
        )
        return await self.create(withdrawal)


    async def get_by_seller_email(self, seller_email: str) -> Optional[SellerWithdrawReservation]:
        """판매자 이메일로 탈퇴 기록 조회"""
        return await self.get_one(seller_email=seller_email)


    async def delete_by_seller_email(self, seller_email: str) -> bool:
        """판매자 이메일로 탈퇴 기록 삭제"""
        withdrawal = await self.get_by_seller_email(seller_email)
        if withdrawal:
            return await self.delete(withdrawal)
        return False


    async def exists_by_seller_email(self, seller_email: str) -> bool:
        """판매자 이메일로 탈퇴 기록 존재 여부 확인"""
        return await self.exists(seller_email=seller_email)