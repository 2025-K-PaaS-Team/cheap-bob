"""/seller/store/settlement — order 도메인의 OrderQueryService 위임."""
from typing import Dict, List
from datetime import date

from app.domain.order.service.order_query import OrderQueryService
from app.database.session import UnitOfWork


class SellerSettlementService:

    def __init__(self, uow: UnitOfWork, order_query_service: OrderQueryService):
        self.uow = uow
        self.order_query_service = order_query_service


    async def get_daily_settlement(
        self, *, store_id: str, start_date: date, end_date: date,
    ) -> List[Dict]:
        return await self.order_query_service.daily_settlement(
            store_id=store_id, start_date=start_date, end_date=end_date,
        )


    async def get_weekly_revenue(self, store_id: str) -> int:
        return await self.order_query_service.weekly_revenue(store_id)
