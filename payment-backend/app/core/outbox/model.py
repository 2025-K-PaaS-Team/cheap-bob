"""Outbox 패턴 모델 — 비즈니스 데이터와 같은 트랜잭션으로 영속화되는 이벤트 큐.

main-backend 의 동일 모듈과 1:1 미러. shared 패턴 미적용 정책 — 양 서비스가 같은 schema 를
자체 정의로 보유. 계약 변경 시 양쪽을 함께 수정.

핵심 전제:
  - `OutboxEvent` 는 비즈니스 테이블과 같은 DB / 같은 트랜잭션에서 INSERT 된다.
  - Kafka 발행은 별도의 `OutboxRelay` (백그라운드 폴링 태스크) 가 담당.
  - `ProcessedEvent` 는 컨슈머 측 멱등성 ledger (PK + INSERT ON CONFLICT DO NOTHING).
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

    - `event_id` UUID: 컨슈머 측 멱등성 키.
    - `aggregate_id`: Kafka 메시지 key — 같은 aggregate 의 이벤트 순서 보장.
    - `published_at` NULL = 미발행. Relay 가 FOR UPDATE SKIP LOCKED 로 잡아간다.
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
        Index(
            "ix_outbox_event_unpublished",
            "id",
            postgresql_where="published_at IS NULL",
        ),
        Index("ix_outbox_event_aggregate", "aggregate_type", "aggregate_id", "id"),
    )


class ProcessedEvent(Base):
    """이미 처리한 이벤트의 ledger — 컨슈머 멱등성 키 저장소."""

    __tablename__ = "processed_event"

    event_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
