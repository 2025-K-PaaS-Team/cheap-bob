"""매일 새벽 전체 상품 재고 (purchased_quantity, admin_adjustment) 리셋 스케줄 작업.

비즈니스 로직은 `SellerProductService.reset_all_inventories()` 에 위치 (UoW + @transactional).
본 모듈은 APScheduler 진입점 + 통계 로깅만 담당.
"""
from typing import Any, Dict
from datetime import datetime, timezone

from app.scheduler.decorators import log_and_swallow
from app.core.logger import get_logger
from app.container import container


logger = get_logger("seller.worker.inventory_reset")


class InventoryResetTask:
    """상품 재고를 초기화하는 스케줄 작업."""

    @staticmethod
    @log_and_swallow("재고 초기화", logger)
    async def reset_inventory():
        logger.info("재고 초기화 작업 시작...")
        start = datetime.now(timezone.utc)
        updated_count = await container.seller_product_service().reset_all_inventories()
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        logger.info(
            "재고 초기화 완료: {}개 ({:.2f}s)", updated_count, elapsed,
        )


    @staticmethod
    async def force_reset_now() -> Dict[str, Any]:
        """수동 실행 (테스트/관리 목적)."""
        logger.info("수동 재고 초기화 요청됨")

        try:
            await InventoryResetTask.reset_inventory()
            return {
                "success": True,
                "message": "재고 초기화가 성공적으로 완료되었습니다",
            }
        except Exception as e:
            logger.exception("수동 재고 초기화 실패")
            return {
                "success": False,
                "message": f"재고 초기화 실패: {e}",
            }


scheduled_task = {
    "func": InventoryResetTask.reset_inventory,
    "trigger": "cron",
    "trigger_args": {
        "hour": 4,
        "minute": 10,
    },
    "job_id": "reset_inventory",
    "job_name": "상품 재고 초기화",
    "misfire_grace_time": 3600,
}
