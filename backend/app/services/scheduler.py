import logging
from pytz import timezone as pytz_timezone
from typing import Dict, Any, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from services.scheduled_tasks.order_migration import scheduled_task as order_migration_task
from services.scheduled_tasks.inventory_reset import scheduled_task as inventory_reset_task


logger = logging.getLogger(__name__)
KST = pytz_timezone('Asia/Seoul')


class SchedulerService:
    """모든 스케줄된 작업을 관리하는 서비스"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.scheduled_tasks: List[Dict[str, Any]] = [
            order_migration_task,
            inventory_reset_task
        ]
    
    def start(self):
        """스케줄러 시작"""
        if not self.is_running:
            self._configure_jobs()
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