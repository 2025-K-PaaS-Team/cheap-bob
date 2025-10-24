from typing import Optional, List
from datetime import datetime, timezone

from database.mongodb_models.product_stock_reservation import ProductStockReservation
from repositories.mongodb_base import BaseMongoRepository


class ProductStockReservationRepository(BaseMongoRepository[ProductStockReservation]):
    """상품 재고 변경 예약 Repository"""
    
    def __init__(self):
        super().__init__(ProductStockReservation)
    
    async def create_reservation(
        self,
        product_id: str,
        initial_stock: int,
        new_stock: int
    ) -> ProductStockReservation:
        """재고 변경 예약 생성 또는 업데이트"""
        existing = await self.get_one(product_id=product_id)
        if existing:
            existing.initial_stock = initial_stock
            existing.new_stock = new_stock
            existing.reserved_at = datetime.now(timezone.utc)
            return await self.update(existing)
        else:
            reservation = ProductStockReservation(
                product_id=product_id,
                initial_stock=initial_stock,
                new_stock=new_stock
            )
            return await self.create(reservation)
    
    async def get_by_product_id(self, product_id: str) -> Optional[ProductStockReservation]:
        """상품 ID로 예약 조회 (고유값)"""
        return await self.get_one(product_id=product_id)
    
    async def get_all_reservations(self, limit: Optional[int] = None) -> List[ProductStockReservation]:
        """모든 예약 조회"""
        return await self.get_many(sort=[("reserved_at", -1)], limit=limit)
    
    async def delete_by_product_id(self, product_id: str) -> bool:
        """상품 ID로 예약 삭제"""
        reservation = await self.get_by_product_id(product_id)
        if reservation:
            return await self.delete(reservation)
        return False