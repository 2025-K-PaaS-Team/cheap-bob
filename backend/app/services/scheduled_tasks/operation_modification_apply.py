import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from database.session import get_db
from database.models.store_operation_info import StoreOperationInfo
from database.models.store_operation_info_modification import StoreOperationInfoModification


logger = logging.getLogger(__name__)

# KST 타임존 설정
KST = timezone(timedelta(hours=9))


class OperationModificationApplyTask:
    """가게 운영 정보 변경 예약을 적용하는 스케줄 작업"""
    
    @staticmethod
    async def apply_operation_modifications():
        """모든 운영 정보 변경 예약을 적용하고 삭제하는 메인 로직"""
        logger.info("가게 운영 정보 변경 예약 적용 작업 시작...")
        start_time = datetime.now(timezone.utc)
        
        applied_count = 0
        error_count = 0
        
        try:
            async for session in get_db():
                query = (
                    select(StoreOperationInfoModification)
                    .options(selectinload(StoreOperationInfoModification.operation_info))
                )
                result = await session.execute(query)
                modifications = result.scalars().all()
                
                total_count = len(modifications)
                
                if total_count == 0:
                    logger.info("적용할 운영 정보 변경 예약이 없습니다.")
                    return
                
                logger.info(f"적용 대상 변경 예약: {total_count}개")
                
                for modification in modifications:
                    try:
                        operation_id = modification.operation_id
                        update_values = {}
                        
                        if modification.new_open_time is not None:
                            update_values['open_time'] = modification.new_open_time
                        if modification.new_close_time is not None:
                            update_values['close_time'] = modification.new_close_time
                        if modification.new_pickup_start_time is not None:
                            update_values['pickup_start_time'] = modification.new_pickup_start_time
                        if modification.new_pickup_end_time is not None:
                            update_values['pickup_end_time'] = modification.new_pickup_end_time
                        if modification.new_is_open_enabled is not None:
                            update_values['is_open_enabled'] = modification.new_is_open_enabled
                        
                        if update_values:
                            stmt = (
                                update(StoreOperationInfo)
                                .where(StoreOperationInfo.operation_id == operation_id)
                                .values(**update_values)
                            )
                            
                            await session.execute(stmt)
                            
                            if modification.operation_info:
                                logger.info(
                                    f"운영 정보 변경 적용 완료 - "
                                    f"가게ID: {modification.operation_info.store_id}, "
                                    f"요일: {modification.operation_info.day_of_week}, "
                                    f"변경내역: {update_values}"
                                )
                            
                            applied_count += 1
                        
                        delete_stmt = (
                            delete(StoreOperationInfoModification)
                            .where(StoreOperationInfoModification.modification_id == modification.modification_id)
                        )
                        await session.execute(delete_stmt)
                        
                    except Exception as e:
                        error_count += 1
                        logger.error(
                            f"운영 정보 변경 적용 실패 - "
                            f"modification_id: {modification.modification_id}, "
                            f"operation_id: {operation_id}, "
                            f"오류: {str(e)}"
                        )
                        continue
                
                await session.commit()
                
                elapsed_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                logger.info(
                    f"가게 운영 정보 변경 예약 적용 완료: "
                    f"전체 {total_count}개 중 {applied_count}개 성공, "
                    f"{error_count}개 실패 "
                    f"(소요시간: {elapsed_time:.2f}초)"
                )
                
                OperationModificationApplyTask._log_apply_statistics(
                    total_count, applied_count, error_count
                )
                
        except Exception as e:
            logger.error(f"가게 운영 정보 변경 예약 적용 중 오류 발생: {e}", exc_info=True)
    
    @staticmethod
    def _log_apply_statistics(total: int, success: int, failed: int):
        """적용 통계 로깅"""
        success_rate = (success / total * 100) if total > 0 else 0
        
        logger.info(
            f"운영 정보 변경 예약 적용 통계 - "
            f"전체: {total}개, "
            f"성공: {success}개 ({success_rate:.1f}%), "
            f"실패: {failed}개, "
            f"적용 시각: {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S KST')}"
        )
    
    @staticmethod
    async def force_apply_now() -> Dict[str, Any]:
        """수동으로 즉시 변경 예약 적용 실행 (테스트/관리 목적)"""
        logger.info("수동 운영 정보 변경 예약 적용 요청됨")
        
        try:
            await OperationModificationApplyTask.apply_operation_modifications()
            return {
                "success": True,
                "message": "운영 정보 변경 예약 적용이 성공적으로 완료되었습니다"
            }
        except Exception as e:
            logger.error(f"수동 운영 정보 변경 예약 적용 실패: {e}")
            return {
                "success": False,
                "message": f"운영 정보 변경 예약 적용 실패: {str(e)}"
            }


# 스케줄러에 등록할 태스크 정의
scheduled_task = {
    "func": OperationModificationApplyTask.apply_operation_modifications,
    "trigger": "cron",
    "trigger_args": {
        "hour": 4,
        "minute": 20,
    },
    "job_id": "apply_operation_modifications",
    "job_name": "가게 운영 정보 변경 예약 적용",
    "misfire_grace_time": 3600,  # 1시간의 유예 시간
}