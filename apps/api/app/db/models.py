from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160), default="")
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    memberships: Mapped[list["WorkspaceMembership"]] = relationship(back_populates="user")


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(160))
    owner_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    workspaces: Mapped[list["Workspace"]] = relationship(back_populates="organization")


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    organization: Mapped[Organization] = relationship(back_populates="workspaces")
    memberships: Mapped[list["WorkspaceMembership"]] = relationship(back_populates="workspace")


class WorkspaceMembership(Base):
    __tablename__ = "workspace_memberships"
    __table_args__ = (UniqueConstraint("workspace_id", "user_id", name="uq_workspace_user"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(String(24), default="owner")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    workspace: Mapped[Workspace] = relationship(back_populates="memberships")
    user: Mapped[User] = relationship(back_populates="memberships")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class BrandRecord(Base):
    __tablename__ = "brand_brains"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    payload: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class ResearchRecord(Base):
    __tablename__ = "research_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    payload: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    workspace_id: Mapped[str | None] = mapped_column(ForeignKey("workspaces.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(120))
    target_type: Mapped[str] = mapped_column(String(80), default="")
    target_id: Mapped[str] = mapped_column(String(120), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Draft(Base):
    __tablename__ = "drafts"
    __table_args__ = (
        Index("ix_drafts_workspace_status_updated", "workspace_id", "status", "updated_at"),
        Index("ix_drafts_workspace_platform_status", "workspace_id", "platform", "status"),
        Index("ix_drafts_workspace_brand", "workspace_id", "brand_id"),
        Index("ix_drafts_workspace_archived", "workspace_id", "archived_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    brand_id: Mapped[str | None] = mapped_column(ForeignKey("brand_brains.id"), nullable=True, index=True)
    source_research_run_id: Mapped[str | None] = mapped_column(ForeignKey("research_runs.id"), nullable=True)
    platform: Mapped[str] = mapped_column(String(40), index=True)
    title: Mapped[str] = mapped_column(String(180))
    body: Mapped[str] = mapped_column(Text)
    hashtags: Mapped[str] = mapped_column(Text, default="[]")
    status: Mapped[str] = mapped_column(String(32), index=True)
    current_version_number: Mapped[int] = mapped_column(Integer, default=1)
    revision: Mapped[int] = mapped_column(Integer, default=1)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    updated_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class DraftVersion(Base):
    __tablename__ = "draft_versions"
    __table_args__ = (UniqueConstraint("draft_id", "version_number", name="uq_draft_version_number"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    draft_id: Mapped[str] = mapped_column(ForeignKey("drafts.id"), index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(180))
    body: Mapped[str] = mapped_column(Text)
    hashtags: Mapped[str] = mapped_column(Text, default="[]")
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    draft_id: Mapped[str] = mapped_column(ForeignKey("drafts.id"), index=True)
    submitted_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    reviewed_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ApprovalComment(Base):
    __tablename__ = "approval_comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    approval_id: Mapped[str] = mapped_column(ForeignKey("approvals.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    comment_type: Mapped[str] = mapped_column(String(32))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Schedule(Base):
    __tablename__ = "schedules"
    __table_args__ = (
        UniqueConstraint("draft_id", "status", name="uq_schedule_draft_status"),
        Index("ix_schedules_workspace_scheduled", "workspace_id", "scheduled_at_utc"),
        Index("ix_schedules_workspace_platform_scheduled", "workspace_id", "platform", "scheduled_at_utc"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    draft_id: Mapped[str] = mapped_column(ForeignKey("drafts.id"), index=True)
    draft_version_id: Mapped[str] = mapped_column(ForeignKey("draft_versions.id"))
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    platform: Mapped[str] = mapped_column(String(40), index=True)
    scheduled_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    workspace_timezone: Mapped[str] = mapped_column(String(80), default="UTC")
    status: Mapped[str] = mapped_column(String(32), index=True)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    updated_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class PublishingJob(Base):
    __tablename__ = "publishing_jobs"
    __table_args__ = (UniqueConstraint("workspace_id", "idempotency_key", name="uq_publishing_job_idempotency"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    draft_id: Mapped[str] = mapped_column(ForeignKey("drafts.id"), index=True)
    draft_version_id: Mapped[str] = mapped_column(ForeignKey("draft_versions.id"))
    schedule_id: Mapped[str | None] = mapped_column(ForeignKey("schedules.id"), nullable=True)
    platform: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(32), index=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(255))
    error_category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    provider_response_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class PublishingAttempt(Base):
    __tablename__ = "publishing_attempts"
    __table_args__ = (UniqueConstraint("job_id", "attempt_number", name="uq_publishing_attempt_number"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    job_id: Mapped[str] = mapped_column(ForeignKey("publishing_jobs.id"), index=True)
    attempt_number: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32))
    provider_post_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    error_category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    provider_response_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class PublishingAuditEvent(Base):
    __tablename__ = "publishing_audit_events"
    __table_args__ = (
        Index("ix_publishing_audit_workspace_job_created", "workspace_id", "job_id", "created_at"),
        Index("ix_publishing_audit_workspace_action", "workspace_id", "action"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    job_id: Mapped[str | None] = mapped_column(ForeignKey("publishing_jobs.id"), nullable=True, index=True)
    draft_id: Mapped[str] = mapped_column(ForeignKey("drafts.id"), index=True)
    draft_version_id: Mapped[str] = mapped_column(ForeignKey("draft_versions.id"))
    provider: Mapped[str] = mapped_column(String(40), default="mock")
    action: Mapped[str] = mapped_column(String(80))
    attempt_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class WorkspacePublishingSettings(Base):
    __tablename__ = "workspace_publishing_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), unique=True, index=True)
    timezone: Mapped[str] = mapped_column(String(80), default="UTC")
    approval_required: Mapped[bool] = mapped_column(Boolean, default=True)
    prevent_self_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    default_platforms: Mapped[str] = mapped_column(Text, default="[]")
    max_retry_count: Mapped[int] = mapped_column(Integer, default=3)
    retry_backoff_base_seconds: Mapped[int] = mapped_column(Integer, default=60)
    queue_concurrency: Mapped[int] = mapped_column(Integer, default=1)
    mock_provider_behavior: Mapped[str] = mapped_column(String(40), default="deterministic")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
