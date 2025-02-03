"""add courage flux column

Revision ID: 7f3a12e4f8d9
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7f3a12e4f8d9'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add the new column with a default value of False
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('courage_flux_approved', sa.Boolean(), nullable=False, server_default='0'))

def downgrade():
    # Remove the column if we need to roll back
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('courage_flux_approved') 