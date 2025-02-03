"""merge heads

Revision ID: merge_heads_456
Revises: 72afe4101a2c, 7f3a12e4f8d9
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'merge_heads_456'
down_revision = ('72afe4101a2c', '7f3a12e4f8d9')
branch_labels = None
depends_on = None

def upgrade():
    # Empty upgrade - just merging branches
    pass

def downgrade():
    # Empty downgrade
    pass 