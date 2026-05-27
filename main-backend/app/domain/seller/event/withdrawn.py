"""seller.store.withdrawn 이벤트 — main-backend (producer) 측 정의.

발행 시점:
  `SellerWithdrawService._hard_delete_seller_with_stores` 의 가게 cascade 삭제 트랜잭션
  안에서 enqueue. 비즈니스 데이터 commit = 이벤트 commit. Kafka 발행은 Relay 가 비동기.

수신자: payment-backend 의 `app.domain.payment.event.seller_withdrawn_handler`.
계약 변경 시 양쪽 동시 수정 — shared 패턴 미적용 정책 (internal_client DTO 와 동일).

aggregate_id = store_id — 같은 가게의 이벤트는 같은 Kafka 파티션 (순서 보장).
"""
from pydantic import BaseModel


# 토픽 — <발행 도메인>.<aggregate>.<event>
TOPIC_SELLER_STORE_WITHDRAWN = "seller.store.withdrawn"

# event_type — 같은 토픽에 향후 다른 이벤트 추가 가능성 대비 명시.
EVENT_TYPE_SELLER_STORE_WITHDRAWN = "SellerStoreWithdrawn"

# schema 버전 — 헤더에 명시. 변경 시 v2 또는 backwards-compatible 필드 추가.
SCHEMA_VERSION = "1"


class SellerStoreWithdrawnPayload(BaseModel):
    """판매자 hard-delete 시 가게(store) 한 개당 1건 발행.

    seller 가 여러 가게를 가졌다면 store 개수만큼 이벤트가 흐른다 (현재 MVP 는 1가게 제약).
    """
    store_id: str
    seller_email: str
