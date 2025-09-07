from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from database.models.order_current_item import OrderCurrentItem
from schemas.seller_order import OrderStatus
from repositories.base import BaseRepository


class OrderCurrentItemRepository(BaseRepository[OrderCurrentItem]):
    """주문 내역 - 당일 보관"""
    def __init__(self, session: AsyncSession):
        super().__init__(OrderCurrentItem, session)
    
    async def get_by_payment_id(self, payment_id: str) -> Optional[OrderCurrentItem]:
        """결제 ID로 조회"""
        return await self.get_by_pk(payment_id)
    
    async def get_by_store_id(self, store_id: str) -> List[OrderCurrentItem]:
        """가게의 현재 주문 목록 조회"""
        return await self.get_many(
            filters={"store_id": store_id},
            order_by=["-order_time"],
            load_relations=["product"]
        )
    
    async def get_by_user_id(self, user_id: str) -> List[OrderCurrentItem]:
        """사용자의 현재 주문 목록 조회"""
        return await self.get_many(
            filters={"user_id": user_id},
            order_by=["-order_time"]
        )
    
    async def get_unprocessed_orders(self, store_id: str) -> List[OrderCurrentItem]:
        """처리되지 않은 주문 조회"""
        return await self.get_many(
            filters={
                "store_id": store_id,
                "status": OrderStatus.reservation
            },
            order_by=["order_time"]
        )
    
    async def accept_order(self, payment_id: str) -> Optional[OrderCurrentItem]:
        """주문 수락 처리"""
        return await self.update(payment_id, status=OrderStatus.accept, accepted_at=datetime.now(timezone.utc))
    
    async def set_pickup_ready(self, payment_id: str) -> Optional[OrderCurrentItem]:
        """픽업 준비 완료 처리"""
        return await self.update(payment_id, status=OrderStatus.pickup, pickup_ready_at=datetime.now(timezone.utc))
    
    async def complete_order(self, payment_id: str) -> Optional[OrderCurrentItem]:
        """픽업 완료 처리"""
        return await self.update(payment_id, status=OrderStatus.complete, completed_at=datetime.now(timezone.utc))

    async def cancel_order(self, payment_id: str) -> int:
        """주문 취소 처리"""
        canceled_item = await self.update(
            payment_id,
            status=OrderStatus.cancel,
            canceled_at=datetime.now(timezone.utc)
        )
        if canceled_item:
            return canceled_item.quantity
    
    async def delete_all_items(self) -> List[OrderCurrentItem]:
        """하루 종료 후, history로 이동하기 위한 삭제"""
        deleted_items = await self.delete_all_and_return()
        return deleted_items
    
    async def migrate_from_current_orders(self, cart_item: dict) -> None:
        """장바구니에서 주문으로 마이그레이션"""
        
        await self.create(
            payment_id=cart_item["payment_id"],
            product_id=cart_item["product_id"],
            user_id=cart_item["user_id"],
            quantity=cart_item["quantity"],
            price=cart_item["price"],
            status=OrderStatus.reservation,
            reservation_at=cart_item.get("order_time", datetime.now(timezone.utc))
        )
        
        return None