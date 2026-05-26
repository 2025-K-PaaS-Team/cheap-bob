"""예약된 상품 재고를 일괄 업데이트하는 스케줄 작업.

비즈니스 로직은 `SellerProductService.apply_pending_stock_updates()` 에 위치
(UoW + @transactional, ProductStockReservationService 위임). 본 모듈은 APScheduler
진입점 + 통계 로깅만 담당.
"""
from datetime import datetime, timezone

from app.scheduler.decorators import log_and_swallow
from app.core.logger import get_logger
from app.container import container


logger = get_logger("seller.worker.product_stock_update")


class ProductStockUpdateTask:
    """Mongo 재고 예약을 SQL 상품 정보에 적용하는 스케줄 작업."""

    @staticmethod
    @log_and_swallow("예약된 재고 업데이트", logger)
    async def update_reserved_stocks():
        start = datetime.now(timezone.utc)
        success, failed = await container.seller_product_service(
        ).apply_pending_stock_updates()
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        logger.info(
            "예약된 재고 업데이트 완료: 성공 {}건, 실패 {}건 ({:.2f}s)",
            success, failed, elapsed,
        )


scheduled_task = {
    "func": ProductStockUpdateTask.update_reserved_stocks,
    "trigger": "cron",
    "trigger_args": {
        "hour": 4,
        "minute": 5,
    },
    "job_id": "update_product_stocks",
    "job_name": "예약된 상품 재고 업데이트",
    "misfire_grace_time": 3600,
}
