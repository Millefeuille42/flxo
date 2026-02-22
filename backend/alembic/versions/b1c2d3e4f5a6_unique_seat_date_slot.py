"""unique seat_date_slot

Revision ID: b1c2d3e4f5a6
Revises: f3c9d2e1b4a5
Create Date: 2026-02-23

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b1c2d3e4f5a6"
down_revision: str | None = "f3c9d2e1b4a5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("presence") as batch_op:
        batch_op.create_unique_constraint(
            "uq_presence_seat_date_slot", ["seat_id", "date", "slot"]
        )


def downgrade() -> None:
    with op.batch_alter_table("presence") as batch_op:
        batch_op.drop_constraint("uq_presence_seat_date_slot", type_="unique")
