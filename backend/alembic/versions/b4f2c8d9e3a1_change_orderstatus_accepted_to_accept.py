"""Change OrderStatus 'accepted' to 'accept'

Revision ID: b4f2c8d9e3a1
Revises: a4456cc53bfb
Create Date: 2025-09-10 12:49:41.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4f2c8d9e3a1'
down_revision: Union[str, Sequence[str], None] = 'a4456cc53bfb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Change enum value from 'accepted' to 'accept' in OrderStatus."""
    # 1. Create new temporary enum type with correct values
    op.execute("CREATE TYPE orderstatus_temp AS ENUM ('reservation', 'accept', 'pickup', 'complete', 'cancel')")
    
    # 2. Update order_current_items table to use new enum type
    op.execute("""
        ALTER TABLE order_current_items 
        ALTER COLUMN status TYPE orderstatus_temp 
        USING CASE 
            WHEN status::text = 'accepted' THEN 'accept'::orderstatus_temp
            ELSE status::text::orderstatus_temp
        END
    """)
    
    # 3. Update order_history_items table to use new enum type
    op.execute("""
        ALTER TABLE order_history_items 
        ALTER COLUMN status TYPE orderstatus_temp 
        USING CASE 
            WHEN status::text = 'accepted' THEN 'accept'::orderstatus_temp
            ELSE status::text::orderstatus_temp
        END
    """)
    
    # 4. Drop old enum type
    op.execute("DROP TYPE orderstatus")
    
    # 5. Rename temporary enum type to original name
    op.execute("ALTER TYPE orderstatus_temp RENAME TO orderstatus")


def downgrade() -> None:
    """Revert enum value from 'accept' back to 'accepted' in OrderStatus."""
    # 1. Create temporary enum type with old values
    op.execute("CREATE TYPE orderstatus_temp AS ENUM ('reservation', 'accepted', 'pickup', 'complete', 'cancel')")
    
    # 2. Update order_current_items table to use old enum type
    op.execute("""
        ALTER TABLE order_current_items 
        ALTER COLUMN status TYPE orderstatus_temp 
        USING CASE 
            WHEN status::text = 'accept' THEN 'accepted'::orderstatus_temp
            ELSE status::text::orderstatus_temp
        END
    """)
    
    # 3. Update order_history_items table to use old enum type
    op.execute("""
        ALTER TABLE order_history_items 
        ALTER COLUMN status TYPE orderstatus_temp 
        USING CASE 
            WHEN status::text = 'accept' THEN 'accepted'::orderstatus_temp
            ELSE status::text::orderstatus_temp
        END
    """)
    
    # 4. Drop current enum type
    op.execute("DROP TYPE orderstatus")
    
    # 5. Rename temporary enum type to original name
    op.execute("ALTER TYPE orderstatus_temp RENAME TO orderstatus")