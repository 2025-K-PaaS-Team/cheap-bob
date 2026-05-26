"""msa payment 분리 — store_payment_info / cart_items 테이블 DROP

payment 도메인이 payment-backend 로 분리되면서 main-backend DB 에서 두 테이블을 제거.
운영 데이터 이전은 별도 1회성 스크립트로 처리 (이 마이그레이션 적용 전 반드시).

Revision ID: b8d40f1c6e1a
Revises: a7e3c9d2f4b1
Create Date: 2026-05-26 00:00:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op


revision: str = "b8d40f1c6e1a"
down_revision: Union[str, Sequence[str], None] = "a7e3c9d2f4b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema — cart_items + store_payment_info DROP."""
    # cart_items 의 expires_at 인덱스 → table → store_payment_info 순.
    op.drop_index("ix_cart_items_expires_at", table_name="cart_items")
    op.drop_table("cart_items")
    op.drop_table("store_payment_info")


def downgrade() -> None:
    """Downgrade — 두 테이블을 복원. (개발 환경 전용; 실 데이터는 백업이 있어야 의미 있음)"""
    op.create_table(
        "store_payment_info",
        sa.Column("store_id", sa.String(length=255), nullable=False),
        sa.Column("portone_store_id", sa.String(length=255), nullable=True),
        sa.Column("portone_channel_id", sa.String(length=255), nullable=True),
        sa.Column("portone_secret_key", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["store_id"], ["stores.store_id"]),
        sa.PrimaryKeyConstraint("store_id"),
    )
    op.create_table(
        "cart_items",
        sa.Column("payment_id", sa.String(length=255), nullable=False),
        sa.Column("product_id", sa.String(length=255), nullable=False),
        sa.Column("customer_id", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("sale", sa.Integer(), nullable=True),
        sa.Column("total_amount", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"], ["store_product_info.product_id"],
        ),
        sa.PrimaryKeyConstraint("payment_id"),
    )
    op.create_index(
        "ix_cart_items_expires_at", "cart_items", ["expires_at"], unique=False,
    )
