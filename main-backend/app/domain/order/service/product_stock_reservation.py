"""ProductStockReservation (Mongo) CRUD — seller.Product 가 본 서비스를 호출한다."""
from typing import Optional

from app.domain.order.service.exception import ProductStockReservationNotFoundError
from app.domain.order.repository.product_stock_reservation import (
    ProductStockReservationRepository,
)
from app.domain.order.model.product_stock_reservation import ProductStockReservation


class ProductStockReservationService:

    def __init__(self, reservation_repo: ProductStockReservationRepository):
        self.reservation_repo = reservation_repo


    async def get(self, product_id: str) -> ProductStockReservation:
        reservation = await self.reservation_repo.get_by_product_id(product_id)
        if reservation is None:
            raise ProductStockReservationNotFoundError("재고 예약 정보를 찾을 수 없습니다")
        return reservation


    async def find(self, product_id: str) -> Optional[ProductStockReservation]:
        return await self.reservation_repo.get_by_product_id(product_id)


    async def upsert(
        self, *, product_id: str, initial_stock: int, new_stock: int,
    ) -> ProductStockReservation:
        return await self.reservation_repo.create_reservation(
            product_id=product_id,
            initial_stock=initial_stock,
            new_stock=new_stock,
        )


    async def delete(self, product_id: str) -> None:
        deleted = await self.reservation_repo.delete_by_product_id(product_id)
        if not deleted:
            raise ProductStockReservationNotFoundError("재고 예약 정보를 찾을 수 없습니다")


    async def get_all(self):
        """모든 재고 예약 조회 (스케줄러 worker 호출)."""
        return await self.reservation_repo.get_all_reservations()


    async def delete_silently(self, product_id: str) -> bool:
        """존재 여부와 무관하게 삭제. 미존재 시 False."""
        return await self.reservation_repo.delete_by_product_id(product_id)
