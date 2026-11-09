"""Add phone number to user profiles.

Revision ID: 20261109_0004
Revises: 20261108_0003
Create Date: 2026-11-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261109_0004"
down_revision: Union[str, Sequence[str], None] = "20261108_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("nomor_telepon", sa.String(length=30), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "nomor_telepon")
