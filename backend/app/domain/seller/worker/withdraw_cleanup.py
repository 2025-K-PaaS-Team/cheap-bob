"""seller 탈퇴 예약 정리 worker.

비즈니스 로직은 `SellerWithdrawService.process_pending_withdrawals()` 에 위치
(UoW + @transactional, 가게 자산 cascade 정리 + Seller hard-delete). 본 모듈은
APScheduler 진입점 + 통계 로깅만 담당.
"""
from datetime import datetime, timezone

from app.scheduler.decorators import log_and_swallow
from app.core.logger import get_logger
from app.container import container


logger = get_logger("seller.worker.withdraw_cleanup")


class SellerWithdrawCleanupTask:
    """예약된 seller 탈퇴를 hard-delete 로 확정한다."""

    @staticmethod
    @log_and_swallow("판매자 탈퇴 처리", logger, fallback=0)
    async def process() -> int:
        start = datetime.now(timezone.utc)
        processed = await container.seller_withdraw_service(
        ).process_pending_withdrawals()
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        logger.info("판매자 탈퇴 처리 완료: {}명 ({:.2f}s)", processed, elapsed)
        return processed


scheduled_task = {
    "func": SellerWithdrawCleanupTask.process,
    "trigger": "cron",
    "trigger_args": {"hour": 4, "minute": 40},
    "job_id": "process_seller_withdrawals",
    "job_name": "예약된 판매자 탈퇴 처리",
    "misfire_grace_time": 3600,
}
