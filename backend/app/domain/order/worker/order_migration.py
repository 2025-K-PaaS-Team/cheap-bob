"""주문 데이터를 현재 테이블에서 히스토리(Mongo) 로 마이그레이션하는 스케줄 작업.

비즈니스 로직은 `OrderQueryService.migrate_finished_orders_to_history()` 에 위치
(UoW + @transactional). 본 모듈은 APScheduler 진입점 + 통계 로깅만 담당.
"""
from datetime import datetime, timezone

from app.core.logger import get_logger
from app.container import container


logger = get_logger("order.worker.order_migration")


class OrderMigrationTask:
    """OrderCurrentItem (SQL) → OrderHistoryItem (Mongo) 이관 스케줄 작업."""

    @staticmethod
    async def migrate_current_orders_to_history():
        start = datetime.now(timezone.utc)
        try:
            archived = await container.order_query_service(
            ).migrate_finished_orders_to_history()
        except Exception:
            logger.exception("주문 마이그레이션 중 오류 발생")
            return

        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        logger.info(
            "주문 마이그레이션 완료: {}건 히스토리로 이동됨 ({:.2f}s)",
            archived, elapsed,
        )


scheduled_task = {
    "func": OrderMigrationTask.migrate_current_orders_to_history,
    "trigger": "cron",
    "trigger_args": {
        "hour": 4,
        "minute": 15,
    },
    "job_id": "migrate_daily_orders",
    "job_name": "당일 주문을 히스토리로 이동",
    "misfire_grace_time": 3600,
}
