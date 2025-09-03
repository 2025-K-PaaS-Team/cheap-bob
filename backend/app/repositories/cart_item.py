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
    
    async def get_by_user_id(self, user_id: str) -> List[CartItem]:
        """사용자 ID로 장바구니 조회"""
        return await self.get_many(
            filters={"user_id": user_id},
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
         
    
    # async def get_expired_items(self, expire_minutes: int = 30) -> List[CartItem]:
    #     """만료된 장바구니 항목 조회"""
    #     expire_time = datetime.now() - timedelta(minutes=expire_minutes)
    #     return await self.get_many(
    #         filters={"created_at": {"lt": expire_time}}
    #     )
    
    # async def delete_user_items(self, user_id: str) -> int:
    #     """사용자의 모든 장바구니 항목 삭제"""
    #     return await self.delete_where(user_id=user_id)
    
    # async def get_cart_summary(self, user_id: str) -> dict:
    #     """사용자 장바구니 요약 정보"""
    #     items = await self.get_by_user_id(user_id)
    #     total_price = sum(item.price * item.quantity for item in items)
    #     total_quantity = sum(item.quantity for item in items)
        
    #     return {
    #         "item_count": len(items),
    #         "total_quantity": total_quantity,
    #         "total_price": total_price
    #     }