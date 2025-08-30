from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.order_history_item import OrderHistoryItem, OrderStatus
from repositories.base import BaseRepository


class OrderHistoryItemRepository(BaseRepository[OrderHistoryItem]):
    """주문 내역 - 영구 보관"""
    def __init__(self, session: AsyncSession):
        super().__init__(OrderHistoryItem, session)
    
    async def get_by_payment_id(self, payment_id: str) -> Optional[OrderHistoryItem]:
        """결제 ID로 조회"""
        return await self.get_by_pk(payment_id)
    
    async def get_by_user_id(
        self, 
        user_id: str,
        status: Optional[OrderStatus] = None,
        limit: Optional[int] = None
    ) -> List[OrderHistoryItem]:
        """사용자의 주문 내역 조회"""
        filters = {"user_id": user_id}
        if status:
            filters["status"] = status
        
        return await self.get_many(
            filters=filters,
            order_by=["-created_at"],
            load_relations=["product"],
            limit=limit
        )
    
    async def get_by_product_id(
        self, 
        product_id: str,
        status: Optional[OrderStatus] = None
    ) -> List[OrderHistoryItem]:
        """상품별 주문 내역 조회"""
        filters = {"product_id": product_id}
        if status:
            filters["status"] = status
        
        return await self.get_many(
            filters=filters,
            order_by=["-created_at"]
        )
    
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[str] = None,
        status: Optional[OrderStatus] = None
    ) -> List[OrderHistoryItem]:
        """날짜 범위로 주문 내역 조회"""
        filters = {
            "created_at": {"gte": start_date, "lte": end_date}
        }
        if user_id:
            filters["user_id"] = user_id
        if status:
            filters["status"] = status
        
        return await self.get_many(
            filters=filters,
            order_by=["-created_at"],
            load_relations=["product"]
        )
    
    async def migrate_from_current_orders(self, current_orders: List[dict]) -> None:
        """현재 주문에서 히스토리로 마이그레이션"""
        
        for order_data in current_orders:
            await self.create(
                payment_id=order_data["payment_id"],
                product_id=order_data["product_id"],
                user_id=order_data["user_id"],
                quantity=order_data["quantity"],
                price=order_data["price"],
                status=order_data.get("status"),
                created_at=order_data.get("order_time", datetime.now())
            )
        
        return None