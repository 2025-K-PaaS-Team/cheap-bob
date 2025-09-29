import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from sqlalchemy import update

from database.session import get_db
from database.models.store_operation_info import StoreOperationInfo


logger = logging.getLogger(__name__)

# KST 타임존 설정
KST = timezone(timedelta(hours=9))


class StoreOperationStatusUpdateTask:
    """가게 운영 상태를 업데이트하는 스케줄 작업"""
    
    @staticmethod
    async def update_store_operation_status():
        """전날의 is_open_enabled 값으로 is_currently_open을 업데이트하는 메인 로직"""
        logger.info("가게 운영 상태 업데이트 작업 시작...")
        start_time = datetime.now(timezone.utc)
        
        try:
            now_kst = datetime.now(KST)
            yesterday_kst = now_kst - timedelta(days=1)
            yesterday_day_of_week = yesterday_kst.weekday()
            
            logger.info(
                f"KST 기준 - 현재: {now_kst.strftime('%Y-%m-%d %H:%M:%S')}, "
                f"어제: {yesterday_kst.strftime('%Y-%m-%d')}, "
                f"어제 요일: {yesterday_day_of_week}"
            )
            async for session in get_db():
                stmt = (
                    update(StoreOperationInfo)
                    .where(StoreOperationInfo.day_of_week == yesterday_day_of_week)
                    .values(is_currently_open=StoreOperationInfo.is_open_enabled)
                )
                
                result = await session.execute(stmt)
                updated_count = result.rowcount
                await session.commit()
                
                elapsed_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                logger.info(
                    f"가게 운영 상태 업데이트 완료: "
                    f"{updated_count}개의 가게 운영 정보가 업데이트됨 "
                    f"(소요시간: {elapsed_time:.2f}초)"
                )
                
                # 업데이트 통계 로깅
                StoreOperationStatusUpdateTask._log_update_statistics(
                    updated_count, yesterday_day_of_week
                )
                
        except Exception as e:
            logger.error(f"가게 운영 상태 업데이트 중 오류 발생: {e}", exc_info=True)
    
    @staticmethod
    def _log_update_statistics(updated_count: int, day_of_week: int):
        """업데이트 통계 로깅"""
        day_names = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
        day_name = day_names[day_of_week] if 0 <= day_of_week <= 6 else "알 수 없음"
        
        logger.info(
            f"가게 운영 상태 업데이트 통계 - "
            f"업데이트된 가게 수: {updated_count}, "
            f"대상 요일: {day_name} ({day_of_week}), "
            f"업데이트 시각: {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S KST')}"
        )
    
    @staticmethod
    async def force_update_now() -> Dict[str, Any]:
        """수동으로 즉시 운영 상태 업데이트 실행 (테스트/관리 목적)"""
        logger.info("수동 가게 운영 상태 업데이트 요청됨")
        
        try:
            await StoreOperationStatusUpdateTask.update_store_operation_status()
            return {
                "success": True,
                "message": "가게 운영 상태 업데이트가 성공적으로 완료되었습니다"
            }
        except Exception as e:
            logger.error(f"수동 가게 운영 상태 업데이트 실패: {e}")
            return {
                "success": False,
                "message": f"가게 운영 상태 업데이트 실패: {str(e)}"
            }

# 스케줄러에 등록할 태스크 정의
scheduled_task = {
    "func": StoreOperationStatusUpdateTask.update_store_operation_status,
    "trigger": "cron",
    "trigger_args": {
        "hour": 4,
        "minute": 20,
    },
    "job_id": "update_store_operation_status",
    "job_name": "가게 운영 상태 업데이트",
    "misfire_grace_time": 3600,  # 1시간의 유예 시간
}