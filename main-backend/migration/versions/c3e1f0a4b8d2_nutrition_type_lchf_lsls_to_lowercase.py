"""nutrition type LCHF/LSLS → lchf/lsls 케이싱 정규화.

Python 측 enum 멤버명을 lowercase 로 통일하는 변경에 맞춰 PostgreSQL ENUM type
`nutritiontype` 의 값 'LCHF', 'LSLS' 를 'lchf', 'lsls' 로 RENAME.

PostgreSQL 10+ 의 `ALTER TYPE ... RENAME VALUE` 는 in-place 라 별도의 데이터
UPDATE 가 필요 없다 (기존 컬럼이 자동으로 새 값을 보게 됨).

Revision ID: c3e1f0a4b8d2
Revises: 947d2e807710
Create Date: 2026-05-21
"""
from typing import Sequence, Union
from alembic import op


revision: str = "c3e1f0a4b8d2"
down_revision: Union[str, Sequence[str], None] = "947d2e807710"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE nutritiontype RENAME VALUE 'LCHF' TO 'lchf'")
    op.execute("ALTER TYPE nutritiontype RENAME VALUE 'LSLS' TO 'lsls'")


def downgrade() -> None:
    op.execute("ALTER TYPE nutritiontype RENAME VALUE 'lchf' TO 'LCHF'")
    op.execute("ALTER TYPE nutritiontype RENAME VALUE 'lsls' TO 'LSLS'")
