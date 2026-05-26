from typing import Any, Dict, List, Optional
from datetime import datetime

from app.domain.order.model.order_history_item import OrderHistoryItem
from app.database.mongodb_repository import BaseMongoRepository


class OrderHistoryItemRepository(BaseMongoRepository[OrderHistoryItem]):
    """주문 히스토리 Repository (MongoDB)."""

    def __init__(self):
        super().__init__(OrderHistoryItem)


    async def bulk_archive_orders(self, orders_data: List[Dict[str, Any]]) -> int:
        """OrderCurrentItem (SQL) 의 일괄 dict 입력을 OrderHistoryItem 으로 저장."""
        history_items = [
            OrderHistoryItem(
                payment_id=order.get("payment_id"),
                customer_id=order.get("customer_id"),
                customer_nickname=order.get("customer_nickname"),
                customer_phone_number=order.get("customer_phone_number"),
                product_id=order.get("product_id"),
                product_name=order.get("product_name"),
                store_id=order.get("store_id"),
                store_name=order.get("store_name"),
                quantity=order.get("quantity"),
                price=order.get("price"),
                sale=order.get("sale"),
                total_amount=order.get("total_amount"),
                status=order.get("status", "reservation"),
                reservation_at=order.get("reservation_at"),
                accepted_at=order.get("accepted_at"),
                completed_at=order.get("completed_at"),
                canceled_at=order.get("canceled_at"),
                cancel_reason=order.get("cancel_reason"),
                preferred_menus=order.get("preferred_menus"),
                nutrition_types=order.get("nutrition_types"),
                allergies=order.get("allergies"),
                topping_types=order.get("topping_types"),
            )
            for order in orders_data
        ]
        if not history_items:
            return 0
        await self.create_many(history_items)
        return len(history_items)


    async def get_customer_history(
        self,
        customer_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[OrderHistoryItem]:
        filters: Dict[str, Any] = {"customer_id": customer_id}
        if start_date or end_date:
            date_filter: Dict[str, Any] = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            filters["reservation_at"] = date_filter
        return await self.get_many(
            filters=filters,
            sort=[("reservation_at", -1)],
            limit=limit,
        )


    async def get_store_history(
        self,
        store_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[OrderHistoryItem]:
        filters: Dict[str, Any] = {"store_id": store_id}
        if start_date or end_date:
            date_filter: Dict[str, Any] = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            filters["reservation_at"] = date_filter
        return await self.get_many(
            filters=filters,
            sort=[("reservation_at", -1)],
            limit=limit,
        )
