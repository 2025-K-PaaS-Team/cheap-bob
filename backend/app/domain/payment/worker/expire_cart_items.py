"""만료된 cart_items 을 정리하는 sweeper 워커 — confirm 누락의 안전망.

webhook 미사용 모델에서 본 sweeper 가 결제 누락 복구를 담당한다.
1분마다 실행되어 expires_at <= now() 인 cart_item 을 batch 로:
  - PortOne 측 PAID 면 주문 자동 생성 (= confirm 누락 복구) + 예약 메일 발송
  - 그 외 (결제 안 됨/실패/금액 불일치) → 재고 복구 + cart 삭제
  - PortOne 일시 장애 → 다음 sweep 으로 미룸

분산 안전성:
  - 각 sweeper 호출은 ``SELECT … FOR UPDATE SKIP LOCKED`` 로 row 단위 락 획득.
  - 여러 노드에서 동시에 cron 이 발화해도 같은 cart 를 두 번 처리하지 않음.
  - 각 cart 처리 실패는 SAVEPOINT 격리 + per-item logger — 한 row 실패가 batch 흐름 차단 금지.

이메일 발송은 DB tx 가 commit 된 후에 한다 — 메일 전송 실패가 finalize 결과를 롤백하지 않게.
"""
from datetime import datetime, timezone

from app.core.logger import get_logger
from app.container import container


logger = get_logger("payment.worker.expire_cart_items")


class ExpireCartItemsTask:
    """만료된 cart_items sweeper."""

    _BATCH_LIMIT = 100

    @staticmethod
    async def sweep():
        from app.core.email.notifier import send_reservation_email

        start = datetime.now(timezone.utc)
        try:
            result = await container.customer_payment_service().sweep_expired_carts(
                limit=ExpireCartItemsTask._BATCH_LIMIT,
            )
        except Exception:
            logger.exception("만료 cart sweep 중 오류 발생")
            return

        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        if result.finalized or result.cancelled or result.transient:
            logger.info(
                "만료 cart sweep 완료: finalized={} cancelled={} transient={} ({:.2f}s)",
                result.finalized, result.cancelled, result.transient, elapsed,
            )

        # finalize 된 고객에게 예약 메일 (best-effort). 메일 실패가 DB 결과를 망치지 못하게
        # tx 가 이미 commit 된 본 시점에서 발송한다.
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
        "minute": "*",  # 매분
    },
    "job_id": "expire_cart_items_sweep",
    "job_name": "만료된 cart 정리 sweeper",
    "misfire_grace_time": 60,
}
