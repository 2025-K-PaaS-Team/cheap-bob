from typing import List, Optional

from app.util.id_generator import generate_product_id
from app.domain.seller.service.exception import (
    ProductAlreadyRegisteredError,
    ProductNotFoundError,
    ProductNutritionDuplicateError,
    ProductNutritionNotFoundError,
    ProductStockConflictError,
    ProductStockInsufficientError,
)
from app.domain.seller.repository.store_product_info import (
    StockUpdateResult,
    StoreProductInfoRepository,
)
from app.domain.seller.repository.product_nutrition import ProductNutritionRepository
from app.domain.seller.model.store_product_info import StoreProductInfo
from app.domain.seller.dto.nutrition import NutritionType
from app.domain.order.service.product_stock_reservation import (
    ProductStockReservationService,
)
from app.database.session import UnitOfWork, transactional
from app.config.setting import settings


class SellerProductService:
    """상품 CRUD + 재고 조정 + 영양 정보. 재고 예약은 order 도메인의 service 에 위임."""

    def __init__(
        self,
        uow: UnitOfWork,
        product_stock_reservation_service: ProductStockReservationService,
    ):
        self.uow = uow
        self.product_stock_reservation_service = product_stock_reservation_service


    @transactional
    async def reset_all_inventories(self) -> int:
        """전체 상품 일일 판매량/관리자 조정값을 0 으로 리셋. (스케줄러 worker 호출)

        Returns: 초기화된 row 수.
        """
        return await StoreProductInfoRepository(self._session).reset_all_inventories()


    @transactional
    async def apply_pending_stock_updates(self) -> tuple[int, int]:
        """Mongo ProductStockReservation 의 모든 예약을 SQL StoreProductInfo 에 적용.

        성공 시 reservation 삭제. 한 건 실패는 swallow + per-item logger.

        Returns: (success, failed).
        """
        from app.core.logger import get_logger

        logger = get_logger("seller.service.seller_product")
        reservations = await self.product_stock_reservation_service.get_all()
        if not reservations:
            return 0, 0

        repo = StoreProductInfoRepository(self._session)
        success = 0
        failed = 0
        for reservation in reservations:
            product_id = reservation.product_id
            try:
                product = await repo.get_by_product_id(product_id)
                if product is None:
                    logger.warning("상품을 찾을 수 없습니다 - product_id: {}", product_id)
                    await self.product_stock_reservation_service.delete_silently(
                        product_id,
                    )
                    continue

                result = await repo.set_stock(product_id, reservation.new_stock)
                if result == StockUpdateResult.SUCCESS:
                    await self.product_stock_reservation_service.delete_silently(
                        product_id,
                    )
                    success += 1
                    logger.info(
                        "재고 업데이트 성공 - product_id: {}, initial: {} -> new: {}",
                        product_id, reservation.initial_stock, reservation.new_stock,
                    )
                else:
                    failed += 1
                    logger.error(
                        "재고 업데이트 실패 - product_id: {}, result: {}",
                        product_id, result,
                    )
            except Exception:
                failed += 1
                logger.exception(
                    "재고 업데이트 중 오류 - product_id: {}", product_id,
                )
        return success, failed


    @transactional
    async def create(
        self,
        *,
        store_id: str,
        product_name: str,
        description: str,
        initial_stock: int,
        price: int,
        sale: Optional[int],
        nutrition_types: List[NutritionType],
    ) -> tuple[StoreProductInfo, List[NutritionType]]:
        """MVP 한 가게에 상품 1개 제약."""
        repo = StoreProductInfoRepository(self._session)
        if await repo.get_by_store_id(store_id):
            raise ProductAlreadyRegisteredError("이미 상품이 등록되어 있습니다.")

        return await repo.create_product_with_nutrition(
            product_id=generate_product_id(),
            store_id=store_id,
            product_name=product_name,
            description=description,
            initial_stock=initial_stock,
            price=price,
            sale=sale,
            nutrition_types=nutrition_types,
        )


    @transactional
    async def get(
        self, *, store_id: str, product_id: str,
    ) -> tuple[StoreProductInfo, List[NutritionType]]:
        repo = StoreProductInfoRepository(self._session)
        product = await repo.get_with_nutrition_info(product_id)
        if product is None or product.store_id != store_id:
            raise ProductNotFoundError("상품을 찾을 수 없습니다.")
        nutrition = [n.nutrition_type for n in (product.nutrition_info or [])]
        return product, nutrition


    @transactional
    async def update(
        self,
        *,
        store_id: str,
        product_id: str,
        update_data: dict,
    ) -> tuple[StoreProductInfo, List[NutritionType]]:
        repo = StoreProductInfoRepository(self._session)
        product = await repo.get_by_product_id(product_id)
        if product is None or product.store_id != store_id:
            raise ProductNotFoundError("상품을 찾을 수 없습니다.")

        # sale=0 → None 으로 변환 (sale 삭제 의도).
        if "sale" in update_data and update_data["sale"] == 0:
            update_data["sale"] = None

        if update_data:
            await repo.update(product_id, **update_data)

        return await self._get_with_nutrition(product_id)


    @transactional
    async def find_product(self, product_id: str) -> Optional[StoreProductInfo]:
        """ownership check 없이 상품 조회. cross-domain (payment, order) 진입점."""
        return await StoreProductInfoRepository(self._session).get_by_product_id(
            product_id,
        )


    @transactional
    async def restore_purchased_stock(
        self, *, product_id: str, quantity: int,
    ) -> None:
        """order 가 환불/취소 시 호출. purchased_quantity 를 -quantity 만큼 조정."""
        await self._adjust_purchased(product_id, -quantity)


    @transactional
    async def consume_purchased_stock(
        self, *, product_id: str, quantity: int,
    ) -> None:
        """payment 가 결제 init 시 호출. purchased_quantity 를 +quantity 만큼 조정.

        재고가 모자라면 `ProductStockInsufficientError`. 낙관적 락 충돌이 끝까지 해소되지
        않으면 `ProductStockConflictError`.
        """
        await self._adjust_purchased(product_id, quantity)


    async def _adjust_purchased(self, product_id: str, delta: int) -> None:
        repo = StoreProductInfoRepository(self._session)
        for _ in range(settings.MAX_RETRY_LOCK):
            result = await repo.adjust_purchased_stock(product_id, delta)
            if result == StockUpdateResult.SUCCESS:
                return
            if result == StockUpdateResult.INSUFFICIENT_STOCK:
                raise ProductStockInsufficientError("재고가 부족합니다.")
        raise ProductStockConflictError("재고 변경 중 충돌이 발생했습니다.")


    @transactional
    async def adjust_admin_stock(
        self, *, store_id: str, product_id: str, delta: int,
    ) -> tuple[StoreProductInfo, List[NutritionType]]:
        """판매자 재고 ±1 (낙관적 락 재시도)."""
        repo = StoreProductInfoRepository(self._session)
        product = await repo.get_by_product_id(product_id)
        if product is None or product.store_id != store_id:
            raise ProductNotFoundError("상품을 찾을 수 없습니다.")

        for attempt in range(settings.MAX_RETRY_LOCK):
            result = await repo.adjust_admin_stock(product_id, delta)
            if result == StockUpdateResult.SUCCESS:
                return await self._get_with_nutrition(product_id)
            if result == StockUpdateResult.INSUFFICIENT_STOCK:
                raise ProductStockInsufficientError(
                    "재고를 더 이상 감소시킬 수 없습니다.",
                )

        raise ProductStockConflictError("재고 업데이트 중 충돌이 발생했습니다.")


    async def get_stock_reservation(self, *, store_id: str, product_id: str):
        await self._assert_belongs(product_id=product_id, store_id=store_id)
        return await self.product_stock_reservation_service.get(product_id)


    async def upsert_stock_reservation(
        self, *, store_id: str, product_id: str, new_stock: int,
    ):
        product = await self._assert_belongs(product_id=product_id, store_id=store_id)
        return await self.product_stock_reservation_service.upsert(
            product_id=product_id,
            initial_stock=product.initial_stock,
            new_stock=new_stock,
        )


    async def delete_stock_reservation(self, *, store_id: str, product_id: str) -> None:
        await self._assert_belongs(product_id=product_id, store_id=store_id)
        await self.product_stock_reservation_service.delete(product_id)


    @transactional
    async def _assert_belongs(
        self, *, product_id: str, store_id: str,
    ) -> StoreProductInfo:
        return await self._assert_product_belongs_to_store(product_id, store_id)


    @transactional
    async def add_nutrition(
        self, *, store_id: str, product_id: str, nutrition_types: List[NutritionType],
    ) -> tuple[StoreProductInfo, List[NutritionType]]:
        await self._assert_product_belongs_to_store(product_id, store_id)

        updated_nutrition, duplicates = await ProductNutritionRepository(
            self._session,
        ).add_nutrition_with_validation(
            product_id=product_id, nutrition_types=nutrition_types,
        )
        if duplicates:
            raise ProductNutritionDuplicateError([d.value for d in duplicates])
        return await self._get_with_nutrition(product_id)


    @transactional
    async def remove_nutrition(
        self, *, store_id: str, product_id: str, nutrition_types: List[NutritionType],
    ) -> tuple[StoreProductInfo, List[NutritionType]]:
        await self._assert_product_belongs_to_store(product_id, store_id)

        repo = ProductNutritionRepository(self._session)
        missing: list[NutritionType] = []
        for n in nutrition_types:
            removed = await repo.remove_nutrition_from_product(
                product_id=product_id, nutrition_type=n,
            )
            if not removed:
                missing.append(n)

        if missing:
            raise ProductNutritionNotFoundError([n.value for n in missing])

        return await self._get_with_nutrition(product_id)


    # ───────── private ─────────


    async def _assert_product_belongs_to_store(
        self, product_id: str, store_id: str,
    ) -> StoreProductInfo:
        product = await StoreProductInfoRepository(self._session).get_by_product_id(
            product_id,
        )
        if product is None or product.store_id != store_id:
            raise ProductNotFoundError("상품을 찾을 수 없습니다.")
        return product


    async def _get_with_nutrition(
        self, product_id: str,
    ) -> tuple[StoreProductInfo, List[NutritionType]]:
        product = await StoreProductInfoRepository(
            self._session,
        ).get_with_nutrition_info(product_id)
        nutrition = [n.nutrition_type for n in (product.nutrition_info or [])]
        return product, nutrition
