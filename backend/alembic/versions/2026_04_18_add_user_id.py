"""Add user_id columns for per-tenant row-level ownership.

Revision ID: a1b2c3d4e5f6
Revises: 73540575ac26
Create Date: 2026-04-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "73540575ac26"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Sentinel owner used ONLY to backfill rows created before auth was
# introduced. No real Firebase uid will ever match this string, so the
# rows become invisible to every authenticated user — exactly what we
# want for historical / orphan data in a development database.
_LEGACY_UID = "legacy-pre-auth"


def upgrade() -> None:
    # ── tllm_profiles ──────────────────────────────────────────────────
    with op.batch_alter_table("tllm_profiles") as batch:
        batch.add_column(sa.Column("user_id", sa.String(), nullable=True))
    op.execute(
        sa.text("UPDATE tllm_profiles SET user_id = :uid WHERE user_id IS NULL")
        .bindparams(uid=_LEGACY_UID)
    )
    with op.batch_alter_table("tllm_profiles") as batch:
        batch.alter_column("user_id", existing_type=sa.String(), nullable=False)
        batch.create_index("ix_tllm_profiles_user_id", ["user_id"])

    # ── scan_runs ──────────────────────────────────────────────────────
    with op.batch_alter_table("scan_runs") as batch:
        batch.add_column(sa.Column("user_id", sa.String(), nullable=True))
    op.execute(
        sa.text("UPDATE scan_runs SET user_id = :uid WHERE user_id IS NULL")
        .bindparams(uid=_LEGACY_UID)
    )
    with op.batch_alter_table("scan_runs") as batch:
        batch.alter_column("user_id", existing_type=sa.String(), nullable=False)
        batch.create_index("ix_scan_runs_user_id", ["user_id"])

    # ── prompt_variants (denormalised for defence-in-depth) ────────────
    with op.batch_alter_table("prompt_variants") as batch:
        batch.add_column(sa.Column("user_id", sa.String(), nullable=True))
    # Backfill variants from their parent scan_run.user_id so existing
    # rows stay consistent even though they'll be invisible post-migration.
    op.execute(
        sa.text(
            "UPDATE prompt_variants SET user_id = ("
            "  SELECT user_id FROM scan_runs WHERE scan_runs.id = prompt_variants.scan_run_id"
            ") WHERE user_id IS NULL"
        )
    )
    # Any variant without a matching scan_run gets the legacy sentinel.
    op.execute(
        sa.text("UPDATE prompt_variants SET user_id = :uid WHERE user_id IS NULL")
        .bindparams(uid=_LEGACY_UID)
    )
    with op.batch_alter_table("prompt_variants") as batch:
        batch.alter_column("user_id", existing_type=sa.String(), nullable=False)
        batch.create_index("ix_prompt_variants_user_id", ["user_id"])


def downgrade() -> None:
    with op.batch_alter_table("prompt_variants") as batch:
        batch.drop_index("ix_prompt_variants_user_id")
        batch.drop_column("user_id")
    with op.batch_alter_table("scan_runs") as batch:
        batch.drop_index("ix_scan_runs_user_id")
        batch.drop_column("user_id")
    with op.batch_alter_table("tllm_profiles") as batch:
        batch.drop_index("ix_tllm_profiles_user_id")
        batch.drop_column("user_id")
