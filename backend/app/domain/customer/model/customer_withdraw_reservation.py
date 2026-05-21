from pydantic import Field
from datetime import datetime, timezone

from app.database.mongodb_document import Document


class CustomerWithdrawReservation(Document):
    """소비자 탈퇴 예약 (Beanie Document)."""

    customer_email: str = Field(..., description="소비자 이메일")
    withdrawn_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="탈퇴 신청 시각",
    )


    class Settings:
        name = "customer_withdraw_reservations"
        indexes = [
            [("customer_email", 1)],
            [("withdrawn_at", -1)],
        ]
