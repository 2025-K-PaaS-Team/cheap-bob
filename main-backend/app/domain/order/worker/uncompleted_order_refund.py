"""미완료 주문(reservation, accept 상태)을 일괄 환불 처리하는 스케줄 작업.

비즈니스 로직은 `SellerOrderService.refund_all_uncompleted()` 에 위치
(가게별 group + 환불/취소 처리). 본 모듈은 APScheduler 진입점 + 통계 로깅만 담당.
"""
from datetime import datetime, timezone

from app.scheduler.decorators import log_and_swallow
from app.core.logger import get_logger
from app.container import container


logger = get_logger("order.worker.uncompleted_order_refund")


class UncompletedOrderRefundTask:
    """미완료 주문(reservation, accept) 자동 환불 스케줄 작업."""

    @staticmethod
    @log_and_swallow("미완료 주문 환불 처리", logger)
    async def refund_uncompleted_orders():
        start = datetime.now(timezone.utc)
        started, failed, total_amount = await container.seller_order_service(
        ).refund_all_uncompleted()
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        logger.info(
            "미완료 주문 환불 이벤트 발행 완료: 시작 {}건, 보류 {}건, 총 발행 금액 {:,}원 ({:.2f}s)",
            started, failed, total_amount, elapsed,
        )


scheduled_task = {
    "func": UncompletedOrderRefundTask.refund_uncompleted_orders,
    "trigger": "cron",
    "trigger_args": {
        "hour": 4,
        "minute": 0,
    },
    "job_id": "refund_uncompleted_orders",
    "job_name": "미완료 주문 자동 환불 처리",
    "misfire_grace_time": 3600,
}
