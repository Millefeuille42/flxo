"""rename from_date and to_date to start and end

Revision ID: 1593a8283ba9
Revises: 2b8b6525ecbf
Create Date: 2025-11-14 14:48:55.462080

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1593a8283ba9'
down_revision: Union[str, Sequence[str], None] = '2b8b6525ecbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("presence") as batch:
        batch.add_column(sa.Column('start', sa.DateTime(), nullable=True))
        batch.add_column(sa.Column('end', sa.DateTime(), nullable=True))

    op.execute("UPDATE presence SET start = from_date, end = to_date")

    with op.batch_alter_table("presence") as batch:
        batch.alter_column('start', nullable=False)
        batch.alter_column('end', nullable=False)

        batch.drop_column('from_date')
        batch.drop_column('to_date')


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("presence") as batch:
        batch.add_column(sa.Column('from_date', sa.DateTime(), nullable=True))
        batch.add_column(sa.Column('to_date', sa.DateTime(), nullable=True))

    op.execute("UPDATE presence SET from_date = start, to_date = end")

    with op.batch_alter_table("presence") as batch:
        batch.alter_column('from_date', nullable=False)
        batch.alter_column('to_date', nullable=False)

        batch.drop_column('start')
        batch.drop_column('end')