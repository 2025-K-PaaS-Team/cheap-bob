"""MSA stock_operation_log — payment-svc 호출 멱등성 ledger 추가

(payment_id, op_type) PK 로 consume/restore 의 중복 적용을 차단.
b8d40f1c6e1a (payment 분리 DROP) 다음 단계.

Revision ID: c9a4f7e2b1d3
Revises: b8d40f1c6e1a
Create Date: 2026-05-26 01:00:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op


revision: str = "c9a4f7e2b1d3"
down_revision: Union[str, Sequence[str], None] = "b8d40f1c6e1a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade — stock_operation_log CREATE."""
    op.create_table(
        "stock_operation_log",
        sa.Column("payment_id", sa.String(length=255), nullable=False),
        sa.Column("op_type", sa.String(length=16), nullable=False),
        sa.Column("product_id", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column(
            "applied_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.PrimaryKeyConstraint("payment_id", "op_type"),
    )


def downgrade() -> None:
    op.drop_table("stock_operation_log")
