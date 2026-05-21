"""customer 탈퇴 예약 정리 worker.

매일 새벽 4:40 KST 에 fired — `CustomerWithdrawService.process_pending_withdrawals()` 가
모든 예약을 hard-delete 로 확정한다. 본 모듈은 APScheduler 진입점 + 통계 로깅만 담당.
"""
from datetime import datetime, timezone

from app.core.logger import get_logger
from app.container import container


logger = get_logger("customer.worker.withdraw_cleanup")


class CustomerWithdrawCleanupTask:
    """예약된 customer 탈퇴를 hard-delete 로 확정한다."""

    @staticmethod
    async def process() -> int:
        start = datetime.now(timezone.utc)
        try:
            processed = await container.customer_withdraw_service().process_pending_withdrawals()
        except Exception:
            logger.exception("소비자 탈퇴 처리 중 오류 발생")
            return 0

        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        logger.info("소비자 탈퇴 처리 완료: {}명 ({:.2f}s)", processed, elapsed)
        return processed


scheduled_task = {
    "func": CustomerWithdrawCleanupTask.process,
    "trigger": "cron",
    "trigger_args": {"hour": 4, "minute": 40},
    "job_id": "process_customer_withdrawals",
    "job_name": "예약된 소비자 탈퇴 처리",
    "misfire_grace_time": 3600,
}
