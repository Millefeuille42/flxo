"""presence date+slot+state, user profile fields

Revision ID: f3c9d2e1b4a5
Revises: 4d042d97cc1e
Create Date: 2026-02-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "f3c9d2e1b4a5"
down_revision: Union[str, Sequence[str], None] = "4d042d97cc1e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # --- Create office table (was in models but never migrated) ---
    op.create_table(
        "office",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("address", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- Create seat table ---
    op.create_table(
        "seat",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("office_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["office_id"], ["office.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- Create property table ---
    op.create_table(
        "property",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("value", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("seat_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["seat_id"], ["seat.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- Presence table ---
    # Add new columns (nullable first for SQLite compatibility)
    with op.batch_alter_table("presence", schema=None) as batch_op:
        batch_op.add_column(sa.Column("date", sa.Date(), nullable=True))
        batch_op.add_column(
            sa.Column(
                "slot",
                sqlmodel.sql.sqltypes.AutoString(),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "state",
                sqlmodel.sql.sqltypes.AutoString(),
                nullable=False,
                server_default="confirmed",
            )
        )
        # seat_id and office_id were in the model but not in the DB — add them now
        batch_op.add_column(sa.Column("seat_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("office_id", sa.Integer(), nullable=True))
        # Drop old datetime columns
        batch_op.drop_column("start")
        batch_op.drop_column("end")

    # Backfill date and slot for any existing rows
    op.execute(
        "UPDATE presence SET date = '2000-01-01', slot = 'morning' WHERE date IS NULL"
    )

    # Make date and slot NOT NULL and add unique constraint
    with op.batch_alter_table("presence", schema=None) as batch_op:
        batch_op.alter_column("date", existing_type=sa.Date(), nullable=False)
        batch_op.alter_column(
            "slot",
            existing_type=sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        )
        batch_op.create_unique_constraint(
            "uq_presence_user_date_slot", ["user_id", "date", "slot"]
        )

    # --- User table ---
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("desk_preference_id", sa.Integer(), nullable=True)
        )


def downgrade() -> None:
    """Downgrade schema."""
    # --- User table ---
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("desk_preference_id")

    # --- Presence table ---
    with op.batch_alter_table("presence", schema=None) as batch_op:
        batch_op.drop_constraint("uq_presence_user_date_slot", type_="unique")
        batch_op.add_column(
            sa.Column("start", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(
            sa.Column("end", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.drop_column("office_id")
        batch_op.drop_column("seat_id")
        batch_op.drop_column("state")
        batch_op.drop_column("slot")
        batch_op.drop_column("date")

    # --- Drop tables in reverse dependency order ---
    op.drop_table("property")
    op.drop_table("seat")
    op.drop_table("office")
