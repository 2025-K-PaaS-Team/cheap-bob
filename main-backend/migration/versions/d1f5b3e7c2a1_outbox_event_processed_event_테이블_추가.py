"""outbox_event + processed_event 테이블 추가 — Outbox 패턴 인프라

main-backend 가 비즈니스 데이터 변경과 같은 트랜잭션으로 이벤트를 적재할 outbox_event,
그리고 컨슈머 멱등성 ledger 인 processed_event 를 추가.

Revision ID: d1f5b3e7c2a1
Revises: c9a4f7e2b1d3
Create Date: 2026-05-26 02:00:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op


revision: str = "d1f5b3e7c2a1"
down_revision: Union[str, Sequence[str], None] = "c9a4f7e2b1d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade — outbox_event + processed_event CREATE."""
    op.create_table(
        "outbox_event",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("event_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("aggregate_type", sa.String(length=64), nullable=False),
        sa.Column("aggregate_id", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("topic", sa.String(length=255), nullable=False),
        sa.Column("payload", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column(
            "headers", sa.dialects.postgresql.JSONB(),
            server_default=sa.text("'{}'::jsonb"), nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", name="uq_outbox_event_event_id"),
    )
    # 미발행 행만 부분 인덱싱 — Relay 폴링 쿼리 비용 최소화.
    op.create_index(
        "ix_outbox_event_unpublished",
        "outbox_event",
        ["id"],
        unique=False,
        postgresql_where=sa.text("published_at IS NULL"),
    )
    op.create_index(
        "ix_outbox_event_aggregate",
        "outbox_event",
        ["aggregate_type", "aggregate_id", "id"],
        unique=False,
    )

    op.create_table(
        "processed_event",
        sa.Column("event_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("topic", sa.String(length=255), nullable=False),
        sa.Column(
            "processed_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.PrimaryKeyConstraint("event_id"),
    )


def downgrade() -> None:
    op.drop_table("processed_event")
    op.drop_index("ix_outbox_event_aggregate", table_name="outbox_event")
    op.drop_index(
        "ix_outbox_event_unpublished",
        table_name="outbox_event",
        postgresql_where=sa.text("published_at IS NULL"),
    )
    op.drop_table("outbox_event")
