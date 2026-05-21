from typing import List, Optional
from datetime import datetime, timedelta, timezone

from app.domain.seller.service.exception import (
    StoreNotFoundError,
    StoreOperationReservationNotFoundError,
)
from app.domain.seller.repository.store_operation_info_modification import (
    StoreOperationInfoModificationRepository,
)
from app.domain.seller.repository.store_operation_info import (
    StoreOperationInfoRepository,
)
from app.domain.seller.repository.store import StoreRepository
from app.domain.seller.model.store_operation_info_modification import (
    StoreOperationInfoModification,
)
from app.domain.seller.model.store_operation_info import StoreOperationInfo
from app.domain.seller.model.store import Store
from app.domain.payment.service.store_payment_info import StorePaymentInfoService
from app.database.session import UnitOfWork, transactional


_KST = timezone(timedelta(hours=9))


class SellerStoreSettingsService:
    """가게 주소 + 운영 정보 + 운영 변경 예약 의 CRUD."""

    def __init__(
        self,
        uow: UnitOfWork,
        store_payment_info_service: StorePaymentInfoService,
    ):
        self.uow = uow
        self.store_payment_info_service = store_payment_info_service


    @transactional
    async def update_address(
        self,
        *,
        store_id: str,
        postal_code: str,
        address: str,
        detail_address: str,
        sido: str,
        sigungu: str,
        bname: str,
        lat: str,
        lng: str,
        nearest_station: Optional[str],
        walking_time: Optional[int],
    ) -> Store:
        repo = StoreRepository(self._session)
        store = await repo.update_store_and_address_atomic(
            store_id=store_id,
            postal_code=postal_code,
            address=address,
            detail_address=detail_address,
            sido=sido,
            sigungu=sigungu,
            bname=bname,
            lat=lat,
            lng=lng,
            nearest_station=nearest_station,
            walking_time=walking_time,
        )
        if store is None:
            raise StoreNotFoundError("가게를 찾을 수 없습니다.")
        return store


    @transactional
    async def list_operation(self, store_id: str) -> List[StoreOperationInfo]:
        return await StoreOperationInfoRepository(self._session).get_by_store_id(
            store_id,
        )


    @transactional
    async def list_operation_modifications(
        self, store_id: str,
    ) -> List[StoreOperationInfoModification]:
        return await StoreOperationInfoModificationRepository(
            self._session,
        ).get_by_store_id(store_id)


    @transactional
    async def upsert_operation_modifications(
        self, *, store_id: str, modifications: List[dict],
    ) -> None:
        repo = StoreOperationInfoModificationRepository(self._session)
        existing = await repo.get_by_store_id(store_id)
        if existing:
            await repo.update_modifications_batch(
                store_id=store_id, modifications_data=modifications,
            )
        else:
            await repo.create_modifications_batch(
                store_id=store_id, modifications_data=modifications,
            )


    @transactional
    async def delete_operation_modifications(self, store_id: str) -> None:
        try:
            await StoreOperationInfoModificationRepository(
                self._session,
            ).delete_all_by_store_id(store_id)
        except ValueError as e:
            raise StoreOperationReservationNotFoundError(str(e))


    @transactional
    async def apply_pending_modifications(self) -> tuple[int, int]:
        """모든 운영 정보 변경 예약을 해당 operation_info 에 적용 + 적용한 modification 삭제.

        Returns: (applied, failed). 한 건 실패는 swallow + per-item logger.
        """
        from app.core.logger import get_logger

        logger = get_logger("seller.service.seller_store_settings")
        mod_repo = StoreOperationInfoModificationRepository(self._session)
        op_repo = StoreOperationInfoRepository(self._session)

        modifications = await mod_repo.get_all_with_operation_info()
        if not modifications:
            return 0, 0

        applied = 0
        failed = 0
        for modification in modifications:
            try:
                update_values: dict = {}
                if modification.new_open_time is not None:
                    update_values["open_time"] = modification.new_open_time
                if modification.new_close_time is not None:
                    update_values["close_time"] = modification.new_close_time
                if modification.new_pickup_start_time is not None:
                    update_values["pickup_start_time"] = modification.new_pickup_start_time
                if modification.new_pickup_end_time is not None:
                    update_values["pickup_end_time"] = modification.new_pickup_end_time
                if modification.new_is_open_enabled is not None:
                    update_values["is_open_enabled"] = modification.new_is_open_enabled

                if update_values:
                    await op_repo.apply_modification(
                        modification.operation_id, update_values,
                    )
                    if modification.operation_info:
                        logger.info(
                            "운영 정보 변경 적용 - 가게ID: {}, 요일: {}, 변경: {}",
                            modification.operation_info.store_id,
                            modification.operation_info.day_of_week,
                            update_values,
                        )
                    applied += 1

                await mod_repo.delete_by_modification_id(modification.modification_id)
            except Exception:
                failed += 1
                logger.exception(
                    "운영 정보 변경 적용 실패 - modification_id: {}",
                    modification.modification_id,
                )
        return applied, failed


    @transactional
    async def list_today_open_operations(
        self,
    ) -> List[StoreOperationInfo]:
        """오늘 요일에 운영 중(is_open_enabled=True) 인 모든 operation_info 를 store 와 함께 반환.

        호출자: 스케줄러 worker (auto_cancel / auto_complete dynamic 등록).
        """
        from datetime import datetime, timedelta, timezone

        _KST = timezone(timedelta(hours=9))
        today_dow = datetime.now(_KST).weekday()
        return await StoreOperationInfoRepository(self._session).get_many(
            filters={"day_of_week": today_dow, "is_open_enabled": True},
            load_relations=["store"],
        )


    @transactional
    async def update_today_open_status(self) -> tuple[int, int]:
        """오늘 요일의 모든 StoreOperationInfo 중, 결제(포트원) 정보가 있는 가게만
        `is_currently_open = is_open_enabled` 로 일괄 업데이트.

        Returns: (updated, skipped). store_payment_info 결제 정보가 없는 가게 = skipped.
        """
        today_dow = datetime.now(_KST).weekday()

        op_repo = StoreOperationInfoRepository(self._session)
        op_infos = await op_repo.get_by_day_of_week(today_dow)
        if not op_infos:
            return 0, 0

        store_ids_to_update: list[str] = []
        skipped = 0
        for op in op_infos:
            if await self.store_payment_info_service.has_complete_info(op.store_id):
                store_ids_to_update.append(op.store_id)
            else:
                skipped += 1

        updated = await op_repo.update_today_open_status_for_stores(
            store_ids_to_update, today_dow,
        )
        return updated, skipped
