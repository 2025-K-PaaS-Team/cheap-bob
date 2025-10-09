from datetime import datetime, timezone
from pydantic import Field

from database.mongodb_models.base import Document


class SellerWithdrawReservation(Document):
    """판매자 탈퇴 예약"""
    
    seller_email: str = Field(..., description="판매자 이메일")
    withdrawn_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        description="탈퇴 시간"
    )
    
    class Settings:
        name = "seller_withdraw_reservations"
        indexes = [
            [("seller_email", 1)],
            [("withdrawn_at", -1)],
        ]