"""add other vehicle price

Revision ID: 6be15bebb2ad
Revises: a1b2c3d4e5f6
Create Date: 2026-09-28 12:40:29.264749

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6be15bebb2ad"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "trips",
        sa.Column(
            "other_vehicle_price",
            sa.Numeric(10, 2),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("trips", "other_vehicle_price")