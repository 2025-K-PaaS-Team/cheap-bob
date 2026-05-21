from typing import List, Optional
from datetime import datetime, time, timedelta, timezone

from app.domain.seller.service.exception import (
    StoreNotFoundError,
    StoreOperationReservationNotFoundError,
)
from app.domain.seller.schema.store_settings import (
    StoreOperationModificationResponse,
    StoreOperationReservationResponse,
)
from app.domain.seller.repository.store_operation_info_modification import (
    StoreOperationInfoModificationRepository,
)
from app.domain.seller.repository.store_operation_info import (
    StoreOperationInfoRepository,
)
from app.domain.seller.repository.store_address import StoreAddressRepository
from app.domain.seller.repository.store import StoreRepository
from app.domain.seller.model.store_operation_info_modification import (
    StoreOperationInfoModification,
)
from app.domain.seller.model.store_operation_info import StoreOperationInfo
from app.domain.seller.model.store import Store
from app.domain.payment.service.store_payment_info import StorePaymentInfoService
from app.database.session import UnitOfWork, transactional
from app.core.logger import get_logger


_KST = timezone(timedelta(hours=9))
_DEFAULT_PICKUP_START_INTERVAL = 60
_DEFAULT_PICKUP_END_INTERVAL = 30


logger = get_logger("seller.service.seller_store_settings")


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
        """가게의 주소 컬럼 + StoreAddress row 를 동일 트랜잭션에서 갱신."""
        store_repo = StoreRepository(self._session)
        store = await store_repo.get_with_address(store_id)
        if store is None:
            raise StoreNotFoundError("가게를 찾을 수 없습니다.")

        if store.address_id is not None:
            await StoreAddressRepository(self._session).update(
                store.address_id,
                sido=sido,
                sigungu=sigungu,
                bname=bname,
                lat=lat,
                lng=lng,
                nearest_station=nearest_station,
                walking_time=walking_time,
            )

        await store_repo.update(
            store_id,
            store_postal_code=postal_code,
            store_address=address,
            store_detail_address=detail_address,
        )

        await self._session.refresh(store, ["address"])
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
    async def get_operation_reservation_summary(
        self, store_id: str,
    ) -> StoreOperationReservationResponse:
        """예약된 운영 변경 사항 + 변경 타입 + pickup 간격을 한 번에 계산.

        라우터는 본 메서드 결과를 그대로 응답하면 된다 (시간 산술/분류는 모두 본 메서드 안).
        """
        modifications = await StoreOperationInfoModificationRepository(
            self._session,
        ).get_by_store_id(store_id)
        operations = await StoreOperationInfoRepository(self._session).get_by_store_id(
            store_id,
        )

        if not modifications:
            response_items = [
                StoreOperationModificationResponse(
                    operation_id=info.operation_id,
                    day_of_week=info.day_of_week,
                    new_open_time=info.open_time,
                    new_close_time=info.close_time,
                    new_is_open_enabled=info.is_open_enabled,
                    created_at=info.updated_at,
                )
                for info in sorted(operations, key=lambda x: x.day_of_week)
            ]
            open_op = next((o for o in operations if o.is_open_enabled), None)
            ps, pe = _pickup_intervals_from_operation(open_op)
            return StoreOperationReservationResponse(
                modification_type=0,
                modifications=response_items,
                new_pickup_start_interval=ps,
                new_pickup_end_interval=pe,
            )

        mod_type = _classify_modification_type(modifications, operations)
        open_mod = next((m for m in modifications if m.new_is_open_enabled), None)
        ps, pe = _pickup_intervals_from_modification(open_mod)
        response_items = [
            StoreOperationModificationResponse(
                operation_id=mod.operation_id,
                day_of_week=mod.operation_info.day_of_week,
                new_open_time=mod.new_open_time,
                new_close_time=mod.new_close_time,
                new_is_open_enabled=mod.new_is_open_enabled,
                created_at=mod.created_at,
            )
            for mod in sorted(
                modifications, key=lambda x: x.operation_info.day_of_week,
            )
        ]
        return StoreOperationReservationResponse(
            modification_type=mod_type,
            modifications=response_items,
            new_pickup_start_interval=ps,
            new_pickup_end_interval=pe,
        )


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
    async def list_today_open_operations(self) -> List[StoreOperationInfo]:
        """오늘 요일에 운영 중(is_open_enabled=True) 인 모든 operation_info 를 store 와 함께 반환.

        호출자: 스케줄러 worker (auto_cancel / auto_complete dynamic 등록).
        """
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


def _classify_modification_type(
    modifications: List[StoreOperationInfoModification],
    operations: List[StoreOperationInfo],
) -> int:
    """수정 유형 분류 — 0: 변화없음, 1: 운영시간만, 2: 픽업시간만, 3: 모두."""
    op_map = {info.operation_id: info for info in operations}
    has_time = False
    has_pickup = False
    for mod in modifications:
        origin = op_map.get(mod.operation_id)
        if origin is None:
            continue

        time_changed = (
            mod.new_open_time != origin.open_time
            or mod.new_close_time != origin.close_time
            or mod.new_is_open_enabled != origin.is_open_enabled
        )
        if time_changed:
            has_time = True

        mod_pstart = _minutes_until_close(mod.new_close_time, mod.new_pickup_start_time)
        orig_pstart = _minutes_until_close(origin.close_time, origin.pickup_start_time)
        mod_pend = _minutes_until_close(mod.new_close_time, mod.new_pickup_end_time)
        orig_pend = _minutes_until_close(origin.close_time, origin.pickup_end_time)
        # 운영여부가 같으면서 픽업 간격만 바뀐 경우만 픽업 변경으로 분류.
        if (
            mod.new_is_open_enabled == origin.is_open_enabled
            and (mod_pstart != orig_pstart or mod_pend != orig_pend)
        ):
            has_pickup = True

    if has_time and has_pickup:
        return 3
    if has_pickup:
        return 2
    if has_time:
        return 1
    return 0


def _pickup_intervals_from_operation(
    op: Optional[StoreOperationInfo],
) -> tuple[int, int]:
    """오픈 가능한 첫 operation 기준 (pickup_start_interval, pickup_end_interval) 분 단위."""
    if op is None:
        return _DEFAULT_PICKUP_START_INTERVAL, _DEFAULT_PICKUP_END_INTERVAL
    return (
        _minutes_until_close(op.close_time, op.pickup_start_time),
        _minutes_until_close(op.close_time, op.pickup_end_time),
    )


def _pickup_intervals_from_modification(
    mod: Optional[StoreOperationInfoModification],
) -> tuple[int, int]:
    if mod is None:
        return _DEFAULT_PICKUP_START_INTERVAL, _DEFAULT_PICKUP_END_INTERVAL
    return (
        _minutes_until_close(mod.new_close_time, mod.new_pickup_start_time),
        _minutes_until_close(mod.new_close_time, mod.new_pickup_end_time),
    )


def _minutes_until_close(close_time: time, target_time: time) -> int:
    """`target_time` 이 `close_time` 보다 얼마 전인지 분 단위로 반환 (음수면 close 이후)."""
    today = datetime.today()
    close_dt = datetime.combine(today, close_time)
    target_dt = datetime.combine(today, target_time)
    return int((close_dt - target_dt).total_seconds() // 60)
