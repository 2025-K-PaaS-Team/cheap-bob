"""정적 스케줄러 — payment-svc 전용.

cart_items sweep (만료된 결제 정리) 하나만 등록.
"""
from typing import Any, Dict, List
from datetime import timedelta, timezone
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.domain.payment.worker.expire_cart_items import (
    scheduled_task as expire_cart_items_task,
)
from app.core.logger import get_logger


logger = get_logger("scheduler.static")
_KST = timezone(timedelta(hours=9))


class StaticScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.scheduled_tasks: List[Dict[str, Any]] = [
            expire_cart_items_task,
        ]


    def start(self):
        if self.is_running:
            return
        self._configure_jobs()
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


static_scheduler = StaticScheduler()
