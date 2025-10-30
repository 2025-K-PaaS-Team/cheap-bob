import logging
from functools import partial
from pytz import timezone as pytz_timezone
from typing import Dict, Any, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from services.scheduled_tasks.order_migration import scheduled_task as order_migration_task
from services.scheduled_tasks.product_stock_update import scheduled_task as product_stock_update_task
from services.scheduled_tasks.inventory_reset import scheduled_task as inventory_reset_task
from services.scheduled_tasks.uncompleted_order_refund import scheduled_task as uncompleted_order_refund_task
from services.scheduled_tasks.operation_modification_apply import scheduled_task as store_operation_modification_apply_tasak
from services.scheduled_tasks.store_operation_status_update import scheduled_task as store_operation_status_update_task
from services.scheduled_tasks.auto_cancel_reservation_orders import scheduled_task as store_auto_complete_order_task, AutoCancelReservationOrdersTask
from services.scheduled_tasks.auto_complete_orders import scheduled_task as store_auto_cancel_reservation_order_task, AutoCompleteOrdersTask
from services.scheduled_tasks.user_withdraw_process import scheduled_task as user_withdraw_process_task

logger = logging.getLogger(__name__)
KST = pytz_timezone('Asia/Seoul')


class SchedulerService:
    """모든 스케줄된 작업을 관리하는 서비스"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.scheduled_tasks: List[Dict[str, Any]] = [
            uncompleted_order_refund_task,
            product_stock_update_task,
            inventory_reset_task,
            order_migration_task,
            store_operation_modification_apply_tasak,
            store_operation_status_update_task,
            user_withdraw_process_task
        ]
    
    def start(self):
        """스케줄러 시작"""
        if not self.is_running:
            self._configure_jobs()
            self._configure_auto_cancel_refund_task()
            self._configure_auto_complete_task()
            self.scheduler.start()
            self.is_running = True
            logger.info("스케줄러가 시작되었습니다")
    
    def stop(self):
        """스케줄러 중지"""
        if self.is_running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("스케줄러가 중지되었습니다")
    
    def _configure_jobs(self):
        """로드된 모든 태스크를 스케줄러에 등록"""
        for task in self.scheduled_tasks:
            try:
                if task["trigger"] == "cron":
                    # KST 타임존 적용
                    trigger_args = task.get("trigger_args", {})
                    trigger = CronTrigger(
                        **trigger_args,
                        timezone=KST
                    )

                    self.scheduler.add_job(
                        func=task["func"],
                        trigger=trigger,
                        id=task["job_id"],
                        name=task.get("job_name", task["job_id"]),
                        misfire_grace_time=task.get("misfire_grace_time", 3600)
                    )

                    logger.info(f"태스크 등록됨: {task.get('job_name', task['job_id'])}")
            except Exception as e:
                logger.error(f"태스크 등록 실패 ({task.get('job_id', 'unknown')}): {e}")

    def _configure_auto_cancel_refund_task(self):
        """픽업 마감 시 주문 자동 취소/환불 동적 스케줄 등록 태스크 설정"""
        try:
            trigger_args = store_auto_cancel_reservation_order_task.get("trigger_args", {})
            trigger = CronTrigger(
                **trigger_args,
                timezone=KST
            )

            self.scheduler.add_job(
                func=partial(AutoCancelReservationOrdersTask.register_daily_schedules, self),
                trigger=trigger,
                id="register_auto_cancel_refund_schedules",
                name="픽업 마감 시간 동적 스케줄 등록 (취소/환불)",
                misfire_grace_time=3600
            )

            logger.info("태스크 등록됨: 픽업 마감 시간 동적 스케줄 등록 (취소/환불)")
        except Exception as e:
            logger.error(f"동적 스케줄 등록 태스크 설정 실패 (취소/환불): {e}")

    def _configure_auto_complete_task(self):
        """가게 마감 시 주문 자동 완료 동적 스케줄 등록 태스크 설정"""
        try:
            trigger_args = store_auto_complete_order_task.get("trigger_args", {})
            trigger = CronTrigger(
                **trigger_args,
                timezone=KST
            )

            self.scheduler.add_job(
                func=partial(AutoCompleteOrdersTask.register_daily_schedules, self),
                trigger=trigger,
                id="register_auto_complete_schedules",
                name="가게 마감 시간 동적 스케줄 등록",
                misfire_grace_time=3600
            )

            logger.info("태스크 등록됨: 가게 마감 시간 동적 스케줄 등록")
        except Exception as e:
            logger.error(f"동적 스케줄 등록 태스크 설정 실패: {e}")
    
    def get_jobs_info(self) -> List[Dict[str, Any]]:
        """현재 등록된 모든 작업 정보 반환"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return jobs
    
    async def run_job_now(self, job_id: str) -> Dict[str, Any]:
        """특정 작업을 즉시 실행 (테스트/관리 목적)"""
        job = self.scheduler.get_job(job_id)
        if not job:
            return {
                "success": False,
                "message": f"작업을 찾을 수 없습니다: {job_id}"
            }
        
        try:
            await job.func()
            return {
                "success": True,
                "message": f"작업이 실행되었습니다: {job_id}"
            }
        except Exception as e:
            logger.error(f"작업 실행 실패 ({job_id}): {e}")
            return {
                "success": False,
                "message": f"작업 실행 실패: {str(e)}"
            }


# 싱글톤 인스턴스
scheduler = SchedulerService()