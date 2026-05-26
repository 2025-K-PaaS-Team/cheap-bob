"""initial payment-backend schema — store_payment_info + cart_items

main-backend 의 동일 테이블 (마이그레이션 b8d40f1c6e1a 에서 DROP) 의 자체 DB 버전.
main-backend 측 stores / store_product_info 와의 FK 는 분리된 DB 이므로 제거.

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-26 00:00:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op


revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade — payment-backend 의 모든 테이블 CREATE."""
    op.create_table(
        "store_payment_info",
        sa.Column("store_id", sa.String(length=255), nullable=False),
        sa.Column("portone_store_id", sa.String(length=255), nullable=True),
        sa.Column("portone_channel_id", sa.String(length=255), nullable=True),
        sa.Column("portone_secret_key", sa.String(length=255), nullable=True),
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
        sa.PrimaryKeyConstraint("payment_id"),
    )
    op.create_index(
        "ix_cart_items_product_id", "cart_items", ["product_id"], unique=False,
    )
    op.create_index(
        "ix_cart_items_expires_at", "cart_items", ["expires_at"], unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_cart_items_expires_at", table_name="cart_items")
    op.drop_index("ix_cart_items_product_id", table_name="cart_items")
    op.drop_table("cart_items")
    op.drop_table("store_payment_info")
