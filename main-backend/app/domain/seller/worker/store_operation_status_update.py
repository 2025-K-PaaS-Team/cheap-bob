"""가게 운영 상태(is_currently_open) 일일 업데이트 스케줄 작업.

비즈니스 로직은 `SellerStoreSettingsService.update_today_open_status()` 에 위치
(UoW + @transactional). 본 모듈은 APScheduler 진입점 + 통계 로깅만 담당.
"""
from datetime import datetime, timezone

from app.scheduler.decorators import log_and_swallow
from app.core.logger import get_logger
from app.container import container


logger = get_logger("seller.worker.store_operation_status_update")


class StoreOperationStatusUpdateTask:
    """오늘 요일 기준 가게 운영 상태를 업데이트하는 스케줄 작업."""

    @staticmethod
    @log_and_swallow("가게 운영 상태 업데이트", logger)
    async def update_store_operation_status():
        start = datetime.now(timezone.utc)
        updated, skipped = await container.seller_store_settings_service(
        ).update_today_open_status()
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        logger.info(
            "가게 운영 상태 업데이트 완료: 업데이트 {}건, 건너뜀 {}건 ({:.2f}s)",
            updated, skipped, elapsed,
        )


scheduled_task = {
    "func": StoreOperationStatusUpdateTask.update_store_operation_status,
    "trigger": "cron",
    "trigger_args": {
        "hour": 4,
        "minute": 25,
    },
    "job_id": "update_store_operation_status",
    "job_name": "가게 운영 상태 업데이트",
    "misfire_grace_time": 3600,
}
