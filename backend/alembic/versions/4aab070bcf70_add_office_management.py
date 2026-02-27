"""add office management

Revision ID: c40261f1e644
Revises: 4d042d97cc1e
Create Date: 2026-01-13 10:27:47.330996

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel

from alembic import op

from typing import Union


revision: str = "c40261f1e644"
down_revision: Union[str, Sequence[str], None] = "4d042d97cc1e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "office",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("address", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "seat",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("office_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["office_id"], ["office.id"], name="fk_seat_office"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "property",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("value", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("seat_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["seat_id"], ["seat.id"], name="fk_property_seat"),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("presence", schema=None) as batch_op:
        batch_op.add_column(sa.Column("office_id", sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column("seat_id", sa.Integer(), nullable=False))

        batch_op.create_foreign_key("fk_presence_office", "office", ["office_id"], ["id"])
        batch_op.create_foreign_key("fk_presence_seat", "seat", ["seat_id"], ["id"])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("presence", schema=None) as batch_op:
        batch_op.drop_constraint("fk_presence_office", type_="foreignkey")
        batch_op.drop_constraint("fk_presence_seat", type_="foreignkey")
        batch_op.drop_column("seat_id")
        batch_op.drop_column("office_id")

    op.drop_table("property")
    op.drop_table("seat")
    op.drop_table("office")
