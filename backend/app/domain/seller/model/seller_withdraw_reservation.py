from pydantic import Field
from datetime import datetime, timezone

from app.database.mongodb_document import Document


class SellerWithdrawReservation(Document):
    """판매자 탈퇴 예약 (Beanie Document)."""

    seller_email: str = Field(..., description="판매자 이메일")
    withdrawn_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="탈퇴 신청 시각",
    )


    class Settings:
        name = "seller_withdraw_reservations"
        indexes = [
            [("seller_email", 1)],
            [("withdrawn_at", -1)],
        ]
