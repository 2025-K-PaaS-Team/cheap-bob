"""cart_items.expires_at 컬럼 추가

APScheduler in-memory job 을 대체하는 DB-backed 결제 timeout 패턴.
sweeper worker 가 expires_at <= now() 를 만료로 처리해 분산 배포 안전성 확보.

Revision ID: a7e3c9d2f4b1
Revises: c3e1f0a4b8d2
Create Date: 2026-05-21 00:00:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a7e3c9d2f4b1"
down_revision: Union[str, Sequence[str], None] = "c3e1f0a4b8d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1) 우선 nullable=True 로 추가 — 기존 row 가 있어도 실패하지 않게.
    op.add_column(
        "cart_items",
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 2) 기존 row 의 expires_at 을 created_at + 5분 으로 백필.
    op.execute(
        "UPDATE cart_items SET expires_at = created_at + INTERVAL '5 minutes' "
        "WHERE expires_at IS NULL",
    )

    # 3) 백필 후 NOT NULL 강제.
    op.alter_column("cart_items", "expires_at", nullable=False)

    # 4) sweeper worker 의 SELECT WHERE expires_at <= now() 지원 인덱스.
    op.create_index(
        "ix_cart_items_expires_at", "cart_items", ["expires_at"], unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_cart_items_expires_at", table_name="cart_items")
    op.drop_column("cart_items", "expires_at")
