"""Address 이름 StoreAddress로 변경

Revision ID: 74f193e5cbcd
Revises: b96dec75bca7
Create Date: 2025-09-25 07:42:50.093712

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74f193e5cbcd'
down_revision: Union[str, Sequence[str], None] = 'b96dec75bca7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('stores_address_id_fkey', 'stores', type_='foreignkey')
    
    op.create_table('store_addresses',
        sa.Column('address_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('sido', sa.String(length=50), nullable=False),
        sa.Column('sigungu', sa.String(length=50), nullable=False),
        sa.Column('bname', sa.String(length=50), nullable=False),
        sa.Column('lat', sa.String(length=50), nullable=False),
        sa.Column('lng', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('address_id')
    )
    
    op.execute("""
        INSERT INTO store_addresses (address_id, sido, sigungu, bname, lat, lng)
        SELECT address_id, sido, sigungu, bname, lat, lng FROM addresses
    """)
    
    op.create_foreign_key('stores_address_id_fkey', 'stores', 'store_addresses', ['address_id'], ['address_id'])
    
    op.drop_table('addresses')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('stores_address_id_fkey', 'stores', type_='foreignkey')
    
    op.create_table('addresses',
        sa.Column('address_id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('sido', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.Column('sigungu', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.Column('bname', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.Column('lat', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.Column('lng', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('address_id', name='addresses_pkey')
    )
    
    op.execute("""
        INSERT INTO addresses (address_id, sido, sigungu, bname, lat, lng)
        SELECT address_id, sido, sigungu, bname, lat, lng FROM store_addresses
    """)
    
    op.create_foreign_key('stores_address_id_fkey', 'stores', 'addresses', ['address_id'], ['address_id'])
    
    op.drop_table('store_addresses')