import logging
from datetime import datetime, timezone, timedelta, time

from services.scheduled_tasks.auto_cancel_reservation_orders import AutoCancelReservationOrdersTask
from services.scheduled_tasks.auto_complete_orders import AutoCompleteOrdersTask

logger = logging.getLogger(__name__)

# KST 타임존 설정
KST = timezone(timedelta(hours=9))


class ScheduleRecovery:
    """서버 재시작 시 동적 스케줄을 복원하는 헬퍼 클래스"""
    
    # 새벽 스케줄 실행 시간 정의
    AUTO_CANCEL_SCHEDULE_TIME = time(4, 50)
    AUTO_COMPLETE_SCHEDULE_TIME = time(5, 0) 
    
    # 서버 재시작 시에만 한 번 실행
    _recovery_executed = False
    
    @staticmethod
    async def recover_dynamic_schedules_if_needed(scheduler) -> bool:
        """
        서버 시작 시 동적 스케줄을 조건부로 복원
        
        Returns:
            bool: 복원이 실행되었으면 True, 실행되지 않았으면 False
        """
        if ScheduleRecovery._recovery_executed:
            logger.info("동적 스케줄 복원이 이미 실행되었습니다.")
            return False
            
        ScheduleRecovery._recovery_executed = True
        
        try:
            now_kst = datetime.now(KST)
            current_time = now_kst.time()
            
            logger.info(f"=== 동적 스케줄 복원 시작 === (현재 시간: {now_kst.strftime('%Y-%m-%d %H:%M:%S KST')})")
            
            cancel_schedule_passed = current_time > ScheduleRecovery.AUTO_CANCEL_SCHEDULE_TIME
            complete_schedule_passed = current_time > ScheduleRecovery.AUTO_COMPLETE_SCHEDULE_TIME
            
            if not cancel_schedule_passed and not complete_schedule_passed:
                logger.info("새벽 스케줄 실행 시간 전입니다. 정기 스케줄이 정상 실행될 예정이므로 복원하지 않습니다.")
                return False
            
            recovery_tasks = []
            
            if cancel_schedule_passed:
                recovery_tasks.append(
                    ScheduleRecovery._recover_cancel_schedules(scheduler)
                )
                
            if complete_schedule_passed:
                recovery_tasks.append(
                    ScheduleRecovery._recover_complete_schedules(scheduler)
                )
            
            if recovery_tasks:
                import asyncio
                results = await asyncio.gather(*recovery_tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        task_name = "픽업 마감" if i == 0 else "가게 마감"
                        logger.error(f"{task_name} 스케줄 복원 실패: {result}")
                
            logger.info("=== 동적 스케줄 복원 완료 ===")
            return True
            
        except Exception as e:
            logger.error(f"동적 스케줄 복원 중 예상치 못한 오류: {e}", exc_info=True)
            return False
    
    @staticmethod
    async def _recover_cancel_schedules(scheduler):
        """픽업 마감 스케줄 복원"""
        try:
            logger.info("픽업 마감(auto_cancel) 동적 스케줄 복원 중...")
            
            existing_job = scheduler.scheduler.get_job("register_auto_cancel_refund_schedules")
            if existing_job:
                logger.info("픽업 마감 정기 스케줄이 이미 등록되어 있습니다.")
            
            await AutoCancelReservationOrdersTask.register_daily_schedules(scheduler)
            logger.info("픽업 마감 동적 스케줄 복원 완료")
            
        except Exception as e:
            logger.error(f"픽업 마감 스케줄 복원 실패: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def _recover_complete_schedules(scheduler):
        """가게 마감 스케줄 복원"""
        try:
            logger.info("가게 마감(auto_complete) 동적 스케줄 복원 중...")
            
            existing_job = scheduler.scheduler.get_job("register_auto_complete_schedules")
            if existing_job:
                logger.info("가게 마감 정기 스케줄이 이미 등록되어 있습니다.")
            
            await AutoCompleteOrdersTask.register_daily_schedules(scheduler)
            logger.info("가게 마감 동적 스케줄 복원 완료")
            
        except Exception as e:
            logger.error(f"가게 마감 스케줄 복원 실패: {e}", exc_info=True)
            raise
    
    @staticmethod
    def reset_recovery_flag():
        """테스트나 특수한 경우를 위한 복원 플래그 리셋"""
        ScheduleRecovery._recovery_executed = False
        logger.info("동적 스케줄 복원 플래그가 리셋되었습니다.")