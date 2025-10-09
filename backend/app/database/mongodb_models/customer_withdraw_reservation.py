from datetime import datetime, timezone
from pydantic import Field

from database.mongodb_models.base import Document


class CustomerWithdrawReservation(Document):
    """소비자 탈퇴 예약"""
    
    customer_email: str = Field(..., description="소비자 이메일")
    withdrawn_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        description="탈퇴 시간"
    )
    
    class Settings:
        name = "customer_withdraw_reservations"
        indexes = [
            [("customer_email", 1)],
            [("withdrawn_at", -1)],
        ]