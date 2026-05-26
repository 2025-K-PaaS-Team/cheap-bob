"""만료된 cart_items 정리 sweeper — confirm 누락 안전망.

1분마다 실행. cart_items DB row 단위 SKIP LOCKED 로 분산 안전.
"""
from datetime import datetime, timezone

from app.scheduler.decorators import log_and_swallow
from app.core.logger import get_logger
from app.core.email.notifier import send_reservation_email
from app.container import container


logger = get_logger("payment.worker.expire_cart_items")


class ExpireCartItemsTask:

    _BATCH_LIMIT = 100

    @staticmethod
    @log_and_swallow("만료 cart sweep", logger)
    async def sweep():
        start = datetime.now(timezone.utc)
        result = await container.customer_payment_service().sweep_expired_carts(
            limit=ExpireCartItemsTask._BATCH_LIMIT,
        )
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        if result.finalized or result.cancelled or result.transient:
            logger.info(
                "만료 cart sweep 완료: finalized={} cancelled={} transient={} ({:.2f}s)",
                result.finalized, result.cancelled, result.transient, elapsed,
            )

        # finalize 된 고객 예약 메일 (best-effort).
        for email in result.finalized_customer_emails:
            try:
                await send_reservation_email(email)
            except Exception:
                logger.exception(
                    "sweep finalize 예약 메일 발송 실패 customer={}", email,
                )


scheduled_task = {
    "func": ExpireCartItemsTask.sweep,
    "trigger": "cron",
    "trigger_args": {
        "minute": "*",
    },
    "job_id": "expire_cart_items_sweep",
    "job_name": "만료된 cart 정리 sweeper",
    "misfire_grace_time": 60,
}
