"""가게 운영 정보 변경 예약을 적용하는 스케줄 작업.

비즈니스 로직은 `SellerStoreSettingsService.apply_pending_modifications()` 에 위치
(UoW + @transactional). 본 모듈은 APScheduler 진입점 + 통계 로깅만 담당.
"""
from datetime import datetime, timezone

from app.scheduler.decorators import log_and_swallow
from app.core.logger import get_logger
from app.container import container


logger = get_logger("seller.worker.operation_modification_apply")


class OperationModificationApplyTask:
    """가게 운영 정보 변경 예약을 적용하는 스케줄 작업."""

    @staticmethod
    @log_and_swallow("운영 정보 변경 예약 적용", logger)
    async def apply_operation_modifications():
        start = datetime.now(timezone.utc)
        applied, failed = await container.seller_store_settings_service(
        ).apply_pending_modifications()
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        logger.info(
            "운영 정보 변경 예약 적용 완료: 적용 {}건, 실패 {}건 ({:.2f}s)",
            applied, failed, elapsed,
        )


scheduled_task = {
    "func": OperationModificationApplyTask.apply_operation_modifications,
    "trigger": "cron",
    "trigger_args": {
        "hour": 4,
        "minute": 20,
    },
    "job_id": "apply_operation_modifications",
    "job_name": "가게 운영 정보 변경 예약 적용",
    "misfire_grace_time": 3600,
}
