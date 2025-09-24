from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cart_item import CartItem
from repositories.base import BaseRepository


class CartItemRepository(BaseRepository[CartItem]):
    """장바구니 - 임시 재고 차감"""
    def __init__(self, session: AsyncSession):
        super().__init__(CartItem, session)
    
    async def get_by_payment_id(self, payment_id: str) -> Optional[CartItem]:
        """결제 ID로 조회"""
        return await self.get_by_pk(payment_id)
    
    async def get_by_cutomer_id(self, customer_id: str) -> List[CartItem]:
        """사용자 ID로 장바구니 조회"""
        return await self.get_many(
            filters={"customer_id": customer_id},
            order_by=["-created_at"],
            load_relations=["product"]
        )
    
    async def get_by_product_id(self, product_id: str) -> List[CartItem]:
        """상품 ID로 장바구니 항목 조회"""
        return await self.get_many(
            filters={"product_id": product_id},
            order_by=["-created_at"]
        )
    
    async def delete_paymen_id_and_return_quantity(self, payment_id: str) -> int:
        """결제 ID로 삭제 후, 수량 반환"""
        deleted_item = await self.delete_and_return(payment_id)
        
        if deleted_item:
            return deleted_item.quantity