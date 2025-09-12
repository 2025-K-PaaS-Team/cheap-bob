"""주문_상태_리팩토링_5단계_확장

Revision ID: 3423034ddc8b
Revises: 6f53cccf8295
Create Date: 2025-09-04 14:19:25.905200

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3423034ddc8b'
down_revision: Union[str, Sequence[str], None] = '6f53cccf8295'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # OrderStatus enum 타입 변경
    # 1. 기존 confirmed_at 데이터를 accepted_at으로 마이그레이션 (이미 6f53cccf8295에서 컬럼은 추가됨)
    op.execute("""
        UPDATE order_current_items 
        SET accepted_at = created_at 
        WHERE status = 'complete' AND accepted_at IS NULL
    """)
    
    op.execute("""
        UPDATE order_history_items 
        SET accepted_at = created_at 
        WHERE status = 'complete' AND accepted_at IS NULL
    """)
    
    # 2. 임시 enum 타입 생성
    op.execute("CREATE TYPE orderstatus_new AS ENUM ('reservation', 'accepted', 'pickup', 'complete', 'cancel')")
    
    # 3. 기존 complete 상태를 accepted로 변경 (기존의 complete는 주문 수락을 의미했음)
    op.execute("""
        ALTER TABLE order_current_items 
        ALTER COLUMN status TYPE orderstatus_new 
        USING CASE 
            WHEN status::text = 'complete' THEN 'accepted'::orderstatus_new
            ELSE status::text::orderstatus_new
        END
    """)
    
    op.execute("""
        ALTER TABLE order_history_items 
        ALTER COLUMN status TYPE orderstatus_new 
        USING CASE 
            WHEN status::text = 'complete' THEN 'accepted'::orderstatus_new
            ELSE status::text::orderstatus_new
        END
    """)
    
    # 4. 기존 enum 타입 삭제
    op.execute("DROP TYPE orderstatus")
    
    # 5. 새로운 enum 타입의 이름을 원래대로 변경
    op.execute("ALTER TYPE orderstatus_new RENAME TO orderstatus")


def downgrade() -> None:
    """Downgrade schema."""
    # OrderStatus enum 타입을 원래대로 복원
    # 1. 임시 enum 타입 생성 (원래 3가지 상태)
    op.execute("CREATE TYPE orderstatus_old AS ENUM ('reservation', 'complete', 'cancel')")
    
    # 2. accepted, pickup, complete 상태를 모두 complete로 변경
    op.execute("""
        ALTER TABLE order_current_items 
        ALTER COLUMN status TYPE orderstatus_old 
        USING CASE 
            WHEN status::text IN ('accepted', 'pickup', 'complete') THEN 'complete'::orderstatus_old
            ELSE status::text::orderstatus_old
        END
    """)
    
    op.execute("""
        ALTER TABLE order_history_items 
        ALTER COLUMN status TYPE orderstatus_old 
        USING CASE 
            WHEN status::text IN ('accepted', 'pickup', 'complete') THEN 'complete'::orderstatus_old
            ELSE status::text::orderstatus_old
        END
    """)
    
    # 3. 기존 enum 타입 삭제
    op.execute("DROP TYPE orderstatus")
    
    # 4. 임시 enum 타입의 이름을 원래대로 변경
    op.execute("ALTER TYPE orderstatus_old RENAME TO orderstatus")
