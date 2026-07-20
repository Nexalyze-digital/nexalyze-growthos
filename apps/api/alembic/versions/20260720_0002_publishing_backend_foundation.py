"""publishing backend foundation

Revision ID: 20260720_0002
Revises: 20260719_0001
Create Date: 2026-07-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260720_0002"
down_revision: str | None = "20260719_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "drafts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("workspace_id", sa.String(length=36), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("brand_id", sa.String(length=36), sa.ForeignKey("brand_brains.id"), nullable=True),
        sa.Column("source_research_run_id", sa.String(length=36), sa.ForeignKey("research_runs.id"), nullable=True),
        sa.Column("platform", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("hashtags", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("current_version_number", sa.Integer(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("updated_by_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_drafts_workspace_id", "drafts", ["workspace_id"])
    op.create_index("ix_drafts_brand_id", "drafts", ["brand_id"])
    op.create_index("ix_drafts_platform", "drafts", ["platform"])
    op.create_index("ix_drafts_status", "drafts", ["status"])
    op.create_index("ix_drafts_archived_at", "drafts", ["archived_at"])
    op.create_index("ix_drafts_deleted_at", "drafts", ["deleted_at"])
    op.create_index("ix_drafts_workspace_status_updated", "drafts", ["workspace_id", "status", "updated_at"])
    op.create_index("ix_drafts_workspace_platform_status", "drafts", ["workspace_id", "platform", "status"])
    op.create_index("ix_drafts_workspace_brand", "drafts", ["workspace_id", "brand_id"])
    op.create_index("ix_drafts_workspace_archived", "drafts", ["workspace_id", "archived_at"])

    op.create_table(
        "draft_versions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("draft_id", sa.String(length=36), sa.ForeignKey("drafts.id"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("hashtags", sa.Text(), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("draft_id", "version_number", name="uq_draft_version_number"),
    )
    op.create_index("ix_draft_versions_draft_id", "draft_versions", ["draft_id"])

    op.create_table(
        "approvals",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("draft_id", sa.String(length=36), sa.ForeignKey("drafts.id"), nullable=False),
        sa.Column("submitted_by_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reviewed_by_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_approvals_draft_id", "approvals", ["draft_id"])
    op.create_index("ix_approvals_status", "approvals", ["status"])

    op.create_table(
        "approval_comments",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("approval_id", sa.String(length=36), sa.ForeignKey("approvals.id"), nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("comment_type", sa.String(length=32), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_approval_comments_approval_id", "approval_comments", ["approval_id"])

    op.create_table(
        "schedules",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("draft_id", sa.String(length=36), sa.ForeignKey("drafts.id"), nullable=False),
        sa.Column("draft_version_id", sa.String(length=36), sa.ForeignKey("draft_versions.id"), nullable=False),
        sa.Column("workspace_id", sa.String(length=36), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("platform", sa.String(length=40), nullable=False),
        sa.Column("scheduled_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("workspace_timezone", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("updated_by_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("draft_id", "status", name="uq_schedule_draft_status"),
    )
    op.create_index("ix_schedules_draft_id", "schedules", ["draft_id"])
    op.create_index("ix_schedules_workspace_id", "schedules", ["workspace_id"])
    op.create_index("ix_schedules_platform", "schedules", ["platform"])
    op.create_index("ix_schedules_scheduled_at_utc", "schedules", ["scheduled_at_utc"])
    op.create_index("ix_schedules_status", "schedules", ["status"])
    op.create_index("ix_schedules_workspace_scheduled", "schedules", ["workspace_id", "scheduled_at_utc"])
    op.create_index(
        "ix_schedules_workspace_platform_scheduled",
        "schedules",
        ["workspace_id", "platform", "scheduled_at_utc"],
    )

    op.create_table(
        "publishing_jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("workspace_id", sa.String(length=36), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("draft_id", sa.String(length=36), sa.ForeignKey("drafts.id"), nullable=False),
        sa.Column("draft_version_id", sa.String(length=36), sa.ForeignKey("draft_versions.id"), nullable=False),
        sa.Column("schedule_id", sa.String(length=36), sa.ForeignKey("schedules.id"), nullable=True),
        sa.Column("platform", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("error_category", sa.String(length=80), nullable=True),
        sa.Column("provider_response_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("workspace_id", "idempotency_key", name="uq_publishing_job_idempotency"),
    )
    op.create_index("ix_publishing_jobs_workspace_id", "publishing_jobs", ["workspace_id"])
    op.create_index("ix_publishing_jobs_draft_id", "publishing_jobs", ["draft_id"])
    op.create_index("ix_publishing_jobs_status", "publishing_jobs", ["status"])

    op.create_table(
        "publishing_attempts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("job_id", sa.String(length=36), sa.ForeignKey("publishing_jobs.id"), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("provider_post_id", sa.String(length=120), nullable=True),
        sa.Column("error_category", sa.String(length=80), nullable=True),
        sa.Column("provider_response_summary", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("job_id", "attempt_number", name="uq_publishing_attempt_number"),
    )
    op.create_index("ix_publishing_attempts_job_id", "publishing_attempts", ["job_id"])

    op.create_table(
        "workspace_publishing_settings",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("workspace_id", sa.String(length=36), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("timezone", sa.String(length=80), nullable=False),
        sa.Column("approval_required", sa.Boolean(), nullable=False),
        sa.Column("prevent_self_approval", sa.Boolean(), nullable=False),
        sa.Column("default_platforms", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_workspace_publishing_settings_workspace_id", "workspace_publishing_settings", ["workspace_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_workspace_publishing_settings_workspace_id", table_name="workspace_publishing_settings")
    op.drop_table("workspace_publishing_settings")
    op.drop_index("ix_publishing_attempts_job_id", table_name="publishing_attempts")
    op.drop_table("publishing_attempts")
    op.drop_index("ix_publishing_jobs_status", table_name="publishing_jobs")
    op.drop_index("ix_publishing_jobs_draft_id", table_name="publishing_jobs")
    op.drop_index("ix_publishing_jobs_workspace_id", table_name="publishing_jobs")
    op.drop_table("publishing_jobs")
    op.drop_index("ix_schedules_workspace_platform_scheduled", table_name="schedules")
    op.drop_index("ix_schedules_workspace_scheduled", table_name="schedules")
    op.drop_index("ix_schedules_status", table_name="schedules")
    op.drop_index("ix_schedules_scheduled_at_utc", table_name="schedules")
    op.drop_index("ix_schedules_platform", table_name="schedules")
    op.drop_index("ix_schedules_workspace_id", table_name="schedules")
    op.drop_index("ix_schedules_draft_id", table_name="schedules")
    op.drop_table("schedules")
    op.drop_index("ix_approval_comments_approval_id", table_name="approval_comments")
    op.drop_table("approval_comments")
    op.drop_index("ix_approvals_status", table_name="approvals")
    op.drop_index("ix_approvals_draft_id", table_name="approvals")
    op.drop_table("approvals")
    op.drop_index("ix_draft_versions_draft_id", table_name="draft_versions")
    op.drop_table("draft_versions")
    op.drop_index("ix_drafts_workspace_archived", table_name="drafts")
    op.drop_index("ix_drafts_workspace_brand", table_name="drafts")
    op.drop_index("ix_drafts_workspace_platform_status", table_name="drafts")
    op.drop_index("ix_drafts_workspace_status_updated", table_name="drafts")
    op.drop_index("ix_drafts_deleted_at", table_name="drafts")
    op.drop_index("ix_drafts_archived_at", table_name="drafts")
    op.drop_index("ix_drafts_status", table_name="drafts")
    op.drop_index("ix_drafts_platform", table_name="drafts")
    op.drop_index("ix_drafts_brand_id", table_name="drafts")
    op.drop_index("ix_drafts_workspace_id", table_name="drafts")
    op.drop_table("drafts")
