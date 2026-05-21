"""동적 스케줄러 — 서버 재시작 시 1회성 동적 스케줄 복원.

`StaticScheduler` 가 매일 새벽 일괄 등록하는 픽업/가게 마감 동적 스케줄은 서버 재시작으로 모두 사라진다. 
`DynamicScheduler.recover_if_needed()` 가 현재 시각을 기준으로 이미 지나간 새벽 시각의 task 를 즉시 재등록한다.
"""
from datetime import datetime, time, timedelta, timezone
import asyncio

from app.domain.order.worker.auto_complete_orders import AutoCompleteOrdersTask
from app.domain.order.worker.auto_cancel_reservation_orders import (
    AutoCancelReservationOrdersTask,
)
from app.core.logger import get_logger


logger = get_logger("scheduler.dynamic")
_KST = timezone(timedelta(hours=9))


class DynamicScheduler:
    """서버 재시작 시 동적 스케줄 복원 (1회성)."""

    # 새벽 일괄 등록 task 의 cron 시각 — 이 시각이 지났는데 등록이 안 됐다면 복원 대상.
    AUTO_CANCEL_SCHEDULE_TIME = time(4, 50)
    AUTO_COMPLETE_SCHEDULE_TIME = time(5, 0)

    _recovery_executed = False


    @classmethod
    async def recover_if_needed(cls, scheduler) -> bool:
        """현재 시각 기준으로 지나간 새벽 등록 task 를 즉시 재등록."""
        if cls._recovery_executed:
            logger.info("동적 스케줄 복원이 이미 실행되었습니다.")
            return False
        cls._recovery_executed = True

        try:
            now_kst = datetime.now(_KST)
            current_time = now_kst.time()
            logger.info(
                "=== 동적 스케줄 복원 시작 === (현재: {})",
                now_kst.strftime("%Y-%m-%d %H:%M:%S KST"),
            )

            cancel_passed = current_time > cls.AUTO_CANCEL_SCHEDULE_TIME
            complete_passed = current_time > cls.AUTO_COMPLETE_SCHEDULE_TIME

            if not cancel_passed and not complete_passed:
                logger.info("새벽 스케줄 실행 시간 전 — 복원 불필요.")
                return False

            tasks = []
            if cancel_passed:
                tasks.append(cls._recover_cancel(scheduler))
            if complete_passed:
                tasks.append(cls._recover_complete(scheduler))

            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        name = "픽업 마감" if i == 0 else "가게 마감"
                        logger.error("{} 스케줄 복원 실패: {}", name, result)

            logger.info("=== 동적 스케줄 복원 완료 ===")
            return True
        except Exception:
            logger.exception("동적 스케줄 복원 중 예상치 못한 오류")
            return False


    @classmethod
    async def _recover_cancel(cls, scheduler) -> None:
        try:
            logger.info("픽업 마감(auto_cancel) 동적 스케줄 복원 중...")
            existing = scheduler.scheduler.get_job("register_auto_cancel_refund_schedules")
            if existing:
                logger.info("픽업 마감 정기 스케줄이 이미 등록되어 있습니다.")
            await AutoCancelReservationOrdersTask.register_daily_schedules(scheduler)
            logger.info("픽업 마감 동적 스케줄 복원 완료")
        except Exception:
            logger.exception("픽업 마감 스케줄 복원 실패")
            raise


    @classmethod
    async def _recover_complete(cls, scheduler) -> None:
        try:
            logger.info("가게 마감(auto_complete) 동적 스케줄 복원 중...")
            existing = scheduler.scheduler.get_job("register_auto_complete_schedules")
            if existing:
                logger.info("가게 마감 정기 스케줄이 이미 등록되어 있습니다.")
            await AutoCompleteOrdersTask.register_daily_schedules(scheduler)
            logger.info("가게 마감 동적 스케줄 복원 완료")
        except Exception:
            logger.exception("가게 마감 스케줄 복원 실패")
            raise


    @classmethod
    def reset_recovery_flag(cls) -> None:
        cls._recovery_executed = False
        logger.info("동적 스케줄 복원 플래그가 리셋되었습니다.")
