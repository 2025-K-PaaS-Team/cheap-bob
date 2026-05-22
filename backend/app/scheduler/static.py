"""정적 스케줄러 — cron 트리거 기반 정기 task.

매일/매주 정해진 시각에 실행되는 task 들 (재고 리셋, 운영 정보 자동 갱신, history 이관 등) 을 APScheduler 인스턴스에 등록한다. 동적 1회성 등록은 `app.scheduler.dynamic` 에서 담당.
"""
from typing import Any, Dict, List
from functools import partial
from datetime import timedelta, timezone
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.domain.seller.worker.withdraw_cleanup import (
    scheduled_task as seller_withdraw_cleanup_task,
)
from app.domain.seller.worker.store_operation_status_update import (
    scheduled_task as store_operation_status_update_task,
)
from app.domain.seller.worker.product_stock_update import (
    scheduled_task as product_stock_update_task,
)
from app.domain.seller.worker.operation_modification_apply import (
    scheduled_task as store_operation_modification_apply_task,
)
from app.domain.seller.worker.inventory_reset import (
    scheduled_task as inventory_reset_task,
)
from app.domain.payment.worker.expire_cart_items import (
    scheduled_task as expire_cart_items_task,
)
from app.domain.order.worker.uncompleted_order_refund import (
    scheduled_task as uncompleted_order_refund_task,
)
from app.domain.order.worker.order_migration import (
    scheduled_task as order_migration_task,
)
from app.domain.order.worker.auto_complete_orders import (
    AutoCompleteOrdersTask,
    registration_cron_args as auto_complete_cron_args,
)
from app.domain.order.worker.auto_cancel_reservation_orders import (
    AutoCancelReservationOrdersTask,
    registration_cron_args as auto_cancel_cron_args,
)
from app.domain.customer.worker.withdraw_cleanup import (
    scheduled_task as customer_withdraw_cleanup_task,
)
from app.core.logger import get_logger


logger = get_logger("scheduler.static")
# KST 는 DST 없는 고정 +09:00 — stdlib timezone 으로 충분. dynamic.py / worker 도 동일.
_KST = timezone(timedelta(hours=9))


class StaticScheduler:
    """cron 기반 정기 task 등록 + 동적 등록 worker 의 부트스트랩."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.scheduled_tasks: List[Dict[str, Any]] = [
            uncompleted_order_refund_task,
            product_stock_update_task,
            inventory_reset_task,
            order_migration_task,
            store_operation_modification_apply_task,
            store_operation_status_update_task,
            customer_withdraw_cleanup_task,
            seller_withdraw_cleanup_task,
            expire_cart_items_task,
        ]


    def start(self):
        if self.is_running:
            return
        self._configure_jobs()
        self._configure_auto_cancel_refund_task()
        self._configure_auto_complete_task()
        self.scheduler.start()
        self.is_running = True
        logger.info("StaticScheduler 시작")


    def stop(self):
        if not self.is_running:
            return
        self.scheduler.shutdown(wait=False)
        self.is_running = False
        logger.info("StaticScheduler 중지")


    def _configure_jobs(self):
        """단순 cron task — 매일/매주 정해진 시각에 실행."""
        for task in self.scheduled_tasks:
            try:
                if task["trigger"] != "cron":
                    continue
                trigger = CronTrigger(**task.get("trigger_args", {}), timezone=_KST)
                self.scheduler.add_job(
                    func=task["func"],
                    trigger=trigger,
                    id=task["job_id"],
                    name=task.get("job_name", task["job_id"]),
                    misfire_grace_time=task.get("misfire_grace_time", 3600),
                )
                logger.info("태스크 등록됨: {}", task.get("job_name", task["job_id"]))
            except Exception:
                logger.exception(
                    "태스크 등록 실패 ({})", task.get("job_id", "unknown"),
                )


    def _configure_auto_cancel_refund_task(self):
        """매일 새벽 픽업 마감 시 주문 자동 취소/환불 — 동적 스케줄 일괄 등록 task."""
        try:
            trigger = CronTrigger(**auto_cancel_cron_args, timezone=_KST)
            self.scheduler.add_job(
                func=partial(AutoCancelReservationOrdersTask.register_daily_schedules, self),
                trigger=trigger,
                id="register_auto_cancel_refund_schedules",
                name="픽업 마감 시간 동적 스케줄 등록 (취소/환불)",
                misfire_grace_time=3600,
            )
            logger.info("태스크 등록됨: 픽업 마감 시간 동적 스케줄 등록 (취소/환불)")
        except Exception:
            logger.exception("동적 스케줄 등록 태스크 설정 실패 (취소/환불)")


    def _configure_auto_complete_task(self):
        """매일 새벽 가게 마감 시 주문 자동 완료 — 동적 스케줄 일괄 등록 task."""
        try:
            trigger = CronTrigger(**auto_complete_cron_args, timezone=_KST)
            self.scheduler.add_job(
                func=partial(AutoCompleteOrdersTask.register_daily_schedules, self),
                trigger=trigger,
                id="register_auto_complete_schedules",
                name="가게 마감 시간 동적 스케줄 등록",
                misfire_grace_time=3600,
            )
            logger.info("태스크 등록됨: 가게 마감 시간 동적 스케줄 등록")
        except Exception:
            logger.exception("동적 스케줄 등록 태스크 설정 실패")


    def get_jobs_info(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            }
            for job in self.scheduler.get_jobs()
        ]


    async def run_job_now(self, job_id: str) -> Dict[str, Any]:
        job = self.scheduler.get_job(job_id)
        if not job:
            return {"success": False, "message": f"작업을 찾을 수 없습니다: {job_id}"}
        try:
            await job.func()
            return {"success": True, "message": f"작업이 실행되었습니다: {job_id}"}
        except Exception as e:
            logger.exception("작업 실행 실패 ({})", job_id)
            return {"success": False, "message": f"작업 실행 실패: {e}"}


# 모듈 싱글톤 — main.py / container.py / dynamic.py 가 같은 instance 를 공유.
static_scheduler = StaticScheduler()
