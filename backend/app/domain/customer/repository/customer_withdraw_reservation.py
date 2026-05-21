from typing import List, Optional
from datetime import datetime

from app.domain.customer.model.customer_withdraw_reservation import (
    CustomerWithdrawReservation,
)


class CustomerWithdrawReservationRepository:
    """Beanie 기반. session 인자 불필요."""

    async def save(
        self, *, customer_email: str, withdrawn_at: datetime,
    ) -> CustomerWithdrawReservation:
        reservation = CustomerWithdrawReservation(
            customer_email=customer_email,
            withdrawn_at=withdrawn_at,
        )
        await reservation.insert()
        return reservation


    async def find_by_customer_email(
        self, customer_email: str,
    ) -> Optional[CustomerWithdrawReservation]:
        return await CustomerWithdrawReservation.find_one(
            CustomerWithdrawReservation.customer_email == customer_email,
        )


    async def delete_by_customer_email(self, customer_email: str) -> bool:
        reservation = await self.find_by_customer_email(customer_email)
        if reservation is None:
            return False
        await reservation.delete()
        return True


    async def get_many(self) -> List[CustomerWithdrawReservation]:
        """전체 탈퇴 예약 목록. withdraw_cleanup worker 가 호출."""
        return await CustomerWithdrawReservation.find_all().to_list()


    async def delete_by_id(self, reservation_id: str) -> bool:
        """worker 가 처리 완료된 reservation 의 ObjectId 로 삭제."""
        from beanie import PydanticObjectId
        reservation = await CustomerWithdrawReservation.get(
            PydanticObjectId(reservation_id),
        )
        if reservation is None:
            return False
        await reservation.delete()
        return True
