"""add TZ support

Revision ID: 4d042d97cc1e
Revises: 1593a8283ba9
Create Date: 2025-11-14 16:03:07.388825

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d042d97cc1e'
down_revision: Union[str, Sequence[str], None] = '1593a8283ba9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("presence", schema=None) as batch_op:
        batch_op.alter_column('start',
                              existing_type=sa.DateTime(),
                              nullable=True)
        batch_op.alter_column('end',
                              existing_type=sa.DateTime(),
                              nullable=True)

def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("presence", schema=None) as batch_op:
        batch_op.alter_column('end',
                              existing_type=sa.DateTime(),
                              nullable=False)
        batch_op.alter_column('start',
                              existing_type=sa.DateTime(),
                              nullable=False)
