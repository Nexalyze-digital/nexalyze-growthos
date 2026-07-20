"""publishing processing engine

Revision ID: 20260720_0003
Revises: 20260720_0002
Create Date: 2026-07-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260720_0003"
down_revision: str | None = "20260720_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("workspace_publishing_settings", sa.Column("max_retry_count", sa.Integer(), nullable=False, server_default="3"))
    op.add_column(
        "workspace_publishing_settings",
        sa.Column("retry_backoff_base_seconds", sa.Integer(), nullable=False, server_default="60"),
    )
    op.add_column("workspace_publishing_settings", sa.Column("queue_concurrency", sa.Integer(), nullable=False, server_default="1"))
    op.add_column(
        "workspace_publishing_settings",
        sa.Column("mock_provider_behavior", sa.String(length=40), nullable=False, server_default="deterministic"),
    )
    op.create_table(
        "publishing_audit_events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("workspace_id", sa.String(length=36), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("job_id", sa.String(length=36), sa.ForeignKey("publishing_jobs.id"), nullable=True),
        sa.Column("draft_id", sa.String(length=36), sa.ForeignKey("drafts.id"), nullable=False),
        sa.Column("draft_version_id", sa.String(length=36), sa.ForeignKey("draft_versions.id"), nullable=False),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_publishing_audit_events_workspace_id", "publishing_audit_events", ["workspace_id"])
    op.create_index("ix_publishing_audit_events_job_id", "publishing_audit_events", ["job_id"])
    op.create_index("ix_publishing_audit_events_draft_id", "publishing_audit_events", ["draft_id"])
    op.create_index(
        "ix_publishing_audit_workspace_job_created",
        "publishing_audit_events",
        ["workspace_id", "job_id", "created_at"],
    )
    op.create_index("ix_publishing_audit_workspace_action", "publishing_audit_events", ["workspace_id", "action"])


def downgrade() -> None:
    op.drop_index("ix_publishing_audit_workspace_action", table_name="publishing_audit_events")
    op.drop_index("ix_publishing_audit_workspace_job_created", table_name="publishing_audit_events")
    op.drop_index("ix_publishing_audit_events_draft_id", table_name="publishing_audit_events")
    op.drop_index("ix_publishing_audit_events_job_id", table_name="publishing_audit_events")
    op.drop_index("ix_publishing_audit_events_workspace_id", table_name="publishing_audit_events")
    op.drop_table("publishing_audit_events")
    op.drop_column("workspace_publishing_settings", "mock_provider_behavior")
    op.drop_column("workspace_publishing_settings", "queue_concurrency")
    op.drop_column("workspace_publishing_settings", "retry_backoff_base_seconds")
    op.drop_column("workspace_publishing_settings", "max_retry_count")
