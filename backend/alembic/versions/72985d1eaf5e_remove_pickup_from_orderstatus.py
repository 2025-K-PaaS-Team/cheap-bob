"""Remove pickup from OrderStatus enum

Revision ID: 72985d1eaf5e
Revises: ab926b3beb8c
Create Date: 2025-09-17 16:31:01.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72985d1eaf5e'
down_revision: Union[str, Sequence[str], None] = 'ab926b3beb8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove 'pickup' from OrderStatus enum."""
    # 1. Create new temporary enum type without 'pickup'
    op.execute("CREATE TYPE orderstatus_temp AS ENUM ('reservation', 'accept', 'complete', 'cancel')")
    
    # 2. Update order_current_items table
    # Convert existing 'pickup' status to 'accept'
    op.execute("""
        ALTER TABLE order_current_items 
        ALTER COLUMN status TYPE orderstatus_temp 
        USING CASE 
            WHEN status::text = 'pickup' THEN 'accept'::orderstatus_temp
            ELSE status::text::orderstatus_temp
        END
    """)
    
    # 3. Update order_history_items table
    # Convert existing 'pickup' status to 'accept'
    op.execute("""
        ALTER TABLE order_history_items 
        ALTER COLUMN status TYPE orderstatus_temp 
        USING CASE 
            WHEN status::text = 'pickup' THEN 'accept'::orderstatus_temp
            ELSE status::text::orderstatus_temp
        END
    """)
    
    # 4. Drop old enum type
    op.execute("DROP TYPE orderstatus")
    
    # 5. Rename temporary enum type to original name
    op.execute("ALTER TYPE orderstatus_temp RENAME TO orderstatus")
    
    # Note: pickup_ready_at timestamp columns are preserved
    # They can still be useful to track when an order is ready


def downgrade() -> None:
    """Restore 'pickup' to OrderStatus enum."""
    # 1. Create temporary enum type with 'pickup' included
    op.execute("CREATE TYPE orderstatus_temp AS ENUM ('reservation', 'accept', 'pickup', 'complete', 'cancel')")
    
    # 2. Update order_current_items table
    # Note: We can't restore which 'accept' orders were originally 'pickup'
    # All current 'accept' orders will remain 'accept'
    op.execute("""
        ALTER TABLE order_current_items 
        ALTER COLUMN status TYPE orderstatus_temp 
        USING status::text::orderstatus_temp
    """)
    
    # 3. Update order_history_items table
    op.execute("""
        ALTER TABLE order_history_items 
        ALTER COLUMN status TYPE orderstatus_temp 
        USING status::text::orderstatus_temp
    """)
    
    # 4. Drop current enum type
    op.execute("DROP TYPE orderstatus")
    
    # 5. Rename temporary enum type to original name
    op.execute("ALTER TYPE orderstatus_temp RENAME TO orderstatus")