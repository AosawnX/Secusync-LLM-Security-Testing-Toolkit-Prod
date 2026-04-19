"""Add carrier_text column to scan_runs for file_poisoning attacks.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Nullable — existing scans never had a carrier document and never
    # will, so backfilling is pointless. New file_poisoning scans will
    # populate this from the upload endpoint.
    with op.batch_alter_table("scan_runs") as batch:
        batch.add_column(sa.Column("carrier_text", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("scan_runs") as batch:
        batch.drop_column("carrier_text")
