"""Outbox 패턴 모델 — 비즈니스 데이터와 같은 트랜잭션으로 영속화되는 이벤트 큐.

핵심 전제:
  - `OutboxEvent` 는 비즈니스 테이블과 같은 DB / 같은 트랜잭션에서 INSERT 된다.
    "DB 커밋 = 이벤트 발행 예약" 이 원자적으로 묶이기 때문에 dual-write 가 사라진다.
  - 실제 Kafka 발행은 별도의 `OutboxRelay` (백그라운드 폴링 태스크) 가 담당.
  - `ProcessedEvent` 는 컨슈머 측 멱등성 ledger — at-least-once 발행을 사용자 비즈니스
    레벨에서 정확히 한 번으로 본다. `stock_operation_log` 와 동일 패턴 (PK + INSERT ON
    CONFLICT DO NOTHING).
"""
from uuid import UUID
from typing import Any
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy import BigInteger, DateTime, Index, String
from datetime import datetime

from app.database.session import Base


class OutboxEvent(Base):
    """발행 대기/완료 이벤트.

    - `event_id` UUID: 컨슈머 측 멱등성 키 (수신 측 ProcessedEvent PK).
    - `aggregate_id`: Kafka 메시지 key — 같은 aggregate 의 이벤트 순서 보장 (같은 파티션).
    - `published_at` NULL = 미발행. Relay 가 SELECT ... FOR UPDATE SKIP LOCKED 로 잡아간다.
    """

    __tablename__ = "outbox_event"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    event_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), unique=True, nullable=False,
    )
    aggregate_type: Mapped[str] = mapped_column(String(64), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    headers: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    __table_args__ = (
        # 미발행 이벤트만 부분 인덱싱 — Relay 폴링 쿼리 비용 최소화.
        Index(
            "ix_outbox_event_unpublished",
            "id",
            postgresql_where="published_at IS NULL",
        ),
        Index("ix_outbox_event_aggregate", "aggregate_type", "aggregate_id", "id"),
    )


class ProcessedEvent(Base):
    """이미 처리한 이벤트의 ledger — 컨슈머 멱등성 키 저장소.

    INSERT 가 성공하면 처음 보는 이벤트, ON CONFLICT DO NOTHING 이면 중복.
    같은 트랜잭션 안에서 비즈니스 데이터 변경과 묶어 commit 하면, retry 시 SQL 레벨에서
    중복이 차단된다. `stock_operation_log` 와 같은 멱등화 패턴.
    """

    __tablename__ = "processed_event"

    event_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
