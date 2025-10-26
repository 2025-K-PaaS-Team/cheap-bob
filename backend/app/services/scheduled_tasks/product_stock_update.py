import logging
from datetime import datetime, timezone
from typing import Dict, Any

from database.session import get_session
from repositories.product_stock_reservation import ProductStockReservationRepository
from repositories.store_product_info import StoreProductInfoRepository, StockUpdateResult


logger = logging.getLogger(__name__)


class ProductStockUpdateTask:
    """예약된 상품 재고를 업데이트하는 스케줄 작업"""
    
    @staticmethod
    async def update_reserved_stocks():
        logger.info("예약된 재고 업데이트 작업 시작...")
        start_time = datetime.now(timezone.utc)
        
        success_count = 0
        failed_count = 0
        
        try:
            reservation_repo = ProductStockReservationRepository()
            
            reservations = await reservation_repo.get_all_reservations()
            
            if not reservations:
                logger.info("업데이트할 재고 예약 정보가 없습니다.")
                return
            
            async with get_session() as session:
                product_repo = StoreProductInfoRepository(session)
                
                for reservation in reservations:
                    try:
                        product = await product_repo.get_by_product_id(reservation.product_id)
                        
                        if not product:
                            logger.warning(
                                f"상품을 찾을 수 없습니다 - "
                                f"product_id: {reservation.product_id}"
                            )
                            await reservation_repo.delete_by_product_id(reservation.product_id)
                            continue
                        
                        result = await product_repo.set_stock(
                            reservation.product_id, 
                            reservation.new_stock
                        )
                        
                        if result == StockUpdateResult.SUCCESS:
                            await reservation_repo.delete_by_product_id(reservation.product_id)
                            success_count += 1
                            
                            logger.info(
                                f"재고 업데이트 성공 - "
                                f"product_id: {reservation.product_id}, "
                                f"initial_stock: {reservation.initial_stock} -> "
                                f"new_stock: {reservation.new_stock}"
                            )
                        else:
                            failed_count += 1
                            logger.error(
                                f"재고 업데이트 실패 - "
                                f"product_id: {reservation.product_id}, "
                                f"result: {result}"
                            )
                            
                    except Exception as e:
                        failed_count += 1
                        logger.error(
                            f"재고 업데이트 중 오류 발생 - "
                            f"product_id: {reservation.product_id}, "
                            f"error: {e}",
                            exc_info=True
                        )
                
                await session.commit()
                
            elapsed_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(
                f"예약된 재고 업데이트 완료: "
                f"성공 {success_count}건, 실패 {failed_count}건 "
                f"(소요시간: {elapsed_time:.2f}초)"
            )
            
            # 업데이트 통계 로깅
            ProductStockUpdateTask._log_update_statistics(success_count, failed_count)
            
        except Exception as e:
            logger.error(f"예약된 재고 업데이트 중 오류 발생: {e}", exc_info=True)
    
    @staticmethod
    def _log_update_statistics(success_count: int, failed_count: int):
        """업데이트 통계 로깅"""
        logger.info(
            f"재고 업데이트 통계 - "
            f"성공: {success_count}건, "
            f"실패: {failed_count}건, "
            f"업데이트 시각: {datetime.now(timezone.utc).isoformat()}"
        )
    
    @staticmethod
    async def force_update_now() -> Dict[str, Any]:
        """수동으로 즉시 재고 업데이트 실행 (테스트/관리 목적)"""
        logger.info("수동 재고 업데이트 요청됨")
        
        try:
            await ProductStockUpdateTask.update_reserved_stocks()
            return {
                "success": True,
                "message": "예약된 재고 업데이트가 성공적으로 완료되었습니다"
            }
        except Exception as e:
            logger.error(f"수동 재고 업데이트 실패: {e}")
            return {
                "success": False,
                "message": f"재고 업데이트 실패: {str(e)}"
            }

# 스케줄러에 등록할 태스크 정의
scheduled_task = {
    "func": ProductStockUpdateTask.update_reserved_stocks,
    "trigger": "cron",
    "trigger_args": {
        "hour": 4,
        "minute": 2,
    },
    "job_id": "update_product_stocks",
    "job_name": "예약된 상품 재고 업데이트",
    "misfire_grace_time": 3600,  # 1시간의 유예 시간
}