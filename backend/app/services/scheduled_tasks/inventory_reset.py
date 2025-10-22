import logging
from datetime import datetime, timezone
from typing import Dict, Any

from sqlalchemy import update
from database.session import get_session
from database.models.store_product_info import StoreProductInfo


logger = logging.getLogger(__name__)


class InventoryResetTask:
    """상품 재고를 초기화하는 스케줄 작업"""
    
    @staticmethod
    async def reset_inventory():
        logger.info("재고 초기화 작업 시작...")
        start_time = datetime.now(timezone.utc)
        
        try:
            async with get_session() as session:
                stmt = (
                    update(StoreProductInfo)
                    .values(
                        purchased_quantity=0,
                        admin_adjustment=0,
                        version=StoreProductInfo.version + 1
                    )
                )
                
                result = await session.execute(stmt)
                updated_count = result.rowcount
                await session.commit()
                
                elapsed_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                logger.info(
                    f"재고 초기화 완료: "
                    f"{updated_count}개의 상품 재고가 초기화됨 "
                    f"(소요시간: {elapsed_time:.2f}초)"
                )
                
                # 초기화 통계 로깅
                InventoryResetTask._log_reset_statistics(updated_count)
                
        except Exception as e:
            logger.error(f"재고 초기화 중 오류 발생: {e}", exc_info=True)
    
    @staticmethod
    def _log_reset_statistics(updated_count: int):
        """초기화 통계 로깅"""
        logger.info(
            f"재고 초기화 통계 - "
            f"초기화된 상품 수: {updated_count}, "
            f"초기화 시각: {datetime.now(timezone.utc).isoformat()}"
        )
    
    @staticmethod
    async def force_reset_now() -> Dict[str, Any]:
        """수동으로 즉시 재고 초기화 실행 (테스트/관리 목적)"""
        logger.info("수동 재고 초기화 요청됨")
        
        try:
            await InventoryResetTask.reset_inventory()
            return {
                "success": True,
                "message": "재고 초기화가 성공적으로 완료되었습니다"
            }
        except Exception as e:
            logger.error(f"수동 재고 초기화 실패: {e}")
            return {
                "success": False,
                "message": f"재고 초기화 실패: {str(e)}"
            }

# 스케줄러에 등록할 태스크 정의
scheduled_task = {
    "func": InventoryResetTask.reset_inventory,
    "trigger": "cron",
    "trigger_args": {
        "hour": 4,
        "minute": 5,
    },
    "job_id": "reset_inventory",
    "job_name": "상품 재고 초기화",
    "misfire_grace_time": 3600,  # 1시간의 유예 시간
}