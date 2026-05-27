"""환불 Saga 이벤트 정의 — main-backend (producer + consumer 양쪽) 측.

Saga 흐름:
  1. main-backend (producer) 가 가게 마감 등 대량 환불 트리거 시
     `order.refund.requested` 를 N개 outbox 발행.
  2. payment-backend (consumer) 가 PortOne refund 호출.
  3. payment-backend (producer) 가 결과를 `payment.refund.completed` 또는 `failed` 로 발행.
  4. main-backend (consumer) 가 completed 를 받아 OrderCurrentItem cancel + stock restore.
     failed 는 CRITICAL 로깅 — 자동 보정 불가, 운영자 알람.

payment-backend 의 `app.domain.payment.event.refund` 와 1:1 미러.
shared 패턴 미적용 — 양쪽 동일 schema 자체 정의. 계약 변경 시 양쪽 동시 수정.

partitioning: aggregate_id = payment_id — 같은 결제의 이벤트는 같은 파티션 (순서 보장),
              다른 결제는 병렬 처리.
"""
from typing import Optional
from pydantic import BaseModel


# ───────── 토픽 / 이벤트 타입 / 버전 ─────────


TOPIC_ORDER_REFUND_REQUESTED = "order.refund.requested"
TOPIC_PAYMENT_REFUND_COMPLETED = "payment.refund.completed"
TOPIC_PAYMENT_REFUND_FAILED = "payment.refund.failed"

EVENT_TYPE_ORDER_REFUND_REQUESTED = "OrderRefundRequested"
EVENT_TYPE_PAYMENT_REFUND_COMPLETED = "PaymentRefundCompleted"
EVENT_TYPE_PAYMENT_REFUND_FAILED = "PaymentRefundFailed"

SCHEMA_VERSION = "2"
# v2 변경: customer_id, store_name 추가.
# 이유: refund 성공 후 cancel 이메일을 completed 핸들러가 책임지도록 — 추가 DB lookup 없이
# payload 만으로 발송 가능. 스케줄러 워커가 손수 보내던 send_seller_cancel_email 을 이관.


# ───────── payload schemas ─────────


class OrderRefundRequestedPayload(BaseModel):
    """main-backend → payment-backend: 한 결제에 대한 환불 요청.

    payment-backend 는 store_id 로 자체 store_payment_info 를 lookup 해 secret_key 사용.
    customer_id / store_name / product_id / quantity 는 echo 용 — completed 응답에 다시
    실어 main-backend 의 cancel/restore/이메일 처리에 사용.
    """
    payment_id: str
    store_id: str
    store_name: str
    customer_id: str
    product_id: str
    quantity: int
    reason: str


class PaymentRefundCompletedPayload(BaseModel):
    """payment-backend → main-backend: PortOne 환불 성공 (또는 이미 취소됨).

    requested 페이로드의 모든 필드를 echo — main-backend 가 별도 lookup 없이 처리 가능.
    """
    payment_id: str
    store_id: str
    store_name: str
    customer_id: str
    product_id: str
    quantity: int
    reason: str


class PaymentRefundFailedPayload(BaseModel):
    """payment-backend → main-backend: PortOne 환불 영구 실패.

    Reasons (대표):
      - 가게 결제 설정 누락 / 불완전 (PaymentInfoMissingError / Incomplete)
      - PortOne 4xx (PaymentRefundError, e.g., 결제 없음)
    transient 실패는 raise 로 consumer retry — 본 이벤트는 발행 안 됨.
    """
    payment_id: str
    store_id: str
    error_kind: str  # "config_missing" | "portone_refused"
    error_detail: Optional[str] = None
