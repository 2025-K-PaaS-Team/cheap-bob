"""환불 Saga 이벤트 정의 — payment-backend 측 미러.

main-backend 의 `app.domain.order.event.refund` 와 1:1 동일 schema. shared 미적용 정책.
계약 변경 시 양쪽 동시 수정.
"""
from typing import Optional
from pydantic import BaseModel


TOPIC_ORDER_REFUND_REQUESTED = "order.refund.requested"
TOPIC_PAYMENT_REFUND_COMPLETED = "payment.refund.completed"
TOPIC_PAYMENT_REFUND_FAILED = "payment.refund.failed"

EVENT_TYPE_PAYMENT_REFUND_COMPLETED = "PaymentRefundCompleted"
EVENT_TYPE_PAYMENT_REFUND_FAILED = "PaymentRefundFailed"

SCHEMA_VERSION = "2"
# v2 변경: customer_id, store_name 추가 — main-backend completed 핸들러가 cancel 이메일을
# payload 만으로 발송 가능.


class OrderRefundRequestedPayload(BaseModel):
    """수신 — main-backend 가 보낸 환불 요청."""
    payment_id: str
    store_id: str
    store_name: str
    customer_id: str
    product_id: str
    quantity: int
    reason: str


class PaymentRefundCompletedPayload(BaseModel):
    """발행 — PortOne 환불 성공 (또는 이미 취소됨) 후. requested payload 의 모든 필드 echo."""
    payment_id: str
    store_id: str
    store_name: str
    customer_id: str
    product_id: str
    quantity: int
    reason: str


class PaymentRefundFailedPayload(BaseModel):
    """발행 — 자동 회복 불가 실패 (4xx / 설정 누락 등)."""
    payment_id: str
    store_id: str
    error_kind: str  # "config_missing" | "portone_refused"
    error_detail: Optional[str] = None
