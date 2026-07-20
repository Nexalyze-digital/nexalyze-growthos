from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PublishingPlatform(str, Enum):
    linkedin = "LinkedIn"
    x = "X"
    instagram = "Instagram"
    facebook = "Facebook"


class DraftStatus(str, Enum):
    generated = "generated"
    edited = "edited"
    ready_for_review = "ready_for_review"
    approved = "approved"
    rejected = "rejected"
    scheduled = "scheduled"
    publishing = "publishing"
    published = "published"
    failed = "failed"
    archived = "archived"


class ApprovalStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    revision_requested = "revision_requested"


class CommentType(str, Enum):
    note = "note"
    rejection_reason = "rejection_reason"
    revision_request = "revision_request"


class ScheduleStatus(str, Enum):
    scheduled = "scheduled"
    unscheduled = "unscheduled"
    publishing = "publishing"
    published = "published"
    failed = "failed"


class PublishingJobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    retry_pending = "retry_pending"
    published = "published"
    succeeded = "succeeded"
    failed = "failed"
    dead_letter = "dead_letter"
    cancelled = "cancelled"


class MockProviderBehavior(str, Enum):
    deterministic = "deterministic"
    success = "success"
    transient_failure = "transient_failure"
    permanent_failure = "permanent_failure"


class DraftBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=180)
    body: str = Field(..., min_length=1, max_length=10000)
    platform: PublishingPlatform
    hashtags: list[str] = Field(default_factory=list, max_length=20)
    brand_id: str | None = Field(default=None, max_length=36)
    source_research_run_id: str | None = Field(default=None, max_length=36)

    @field_validator("hashtags")
    @classmethod
    def normalize_hashtags(cls, value: list[str]) -> list[str]:
        normalized = []
        seen = set()
        for item in value:
            tag = item.strip()
            if not tag:
                continue
            if not tag.startswith("#"):
                tag = f"#{tag}"
            if len(tag) > 80:
                raise ValueError("Hashtags must be 80 characters or fewer.")
            lowered = tag.lower()
            if lowered not in seen:
                seen.add(lowered)
                normalized.append(tag)
        return normalized


class DraftCreate(DraftBase):
    pass


class DraftUpdate(DraftBase):
    expected_revision: int = Field(..., ge=1)


class DraftDuplicateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=180)


class DraftVersionResponse(BaseModel):
    id: str
    draft_id: str
    version_number: int
    title: str
    body: str
    hashtags: list[str]
    created_by_user_id: str
    created_at: datetime


class DraftResponse(DraftBase):
    id: str
    workspace_id: str
    status: DraftStatus
    current_version_number: int
    revision: int
    created_by_user_id: str
    updated_by_user_id: str
    archived_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    latest_version: DraftVersionResponse | None = None


class DraftListResponse(BaseModel):
    drafts: list[DraftResponse]
    page: int
    page_size: int
    total: int


class DraftVersionListResponse(BaseModel):
    versions: list[DraftVersionResponse]


class ReviewCommentCreate(BaseModel):
    body: str = Field(..., min_length=2, max_length=2000)


class ApprovalCommentResponse(BaseModel):
    id: str
    approval_id: str
    user_id: str
    comment_type: CommentType
    body: str
    created_at: datetime


class ApprovalResponse(BaseModel):
    id: str
    draft_id: str
    submitted_by_user_id: str
    reviewed_by_user_id: str | None = None
    status: ApprovalStatus
    submitted_at: datetime
    reviewed_at: datetime | None = None
    comments: list[ApprovalCommentResponse] = Field(default_factory=list)


class ReviewHistoryResponse(BaseModel):
    approvals: list[ApprovalResponse]


class ScheduleCreate(BaseModel):
    scheduled_at: datetime
    timezone: str = Field(default="UTC", min_length=1, max_length=80)


class ScheduleUpdate(ScheduleCreate):
    pass


class ScheduleResponse(BaseModel):
    id: str
    draft_id: str
    draft_version_id: str
    workspace_id: str
    platform: PublishingPlatform
    scheduled_at_utc: datetime
    workspace_timezone: str
    status: ScheduleStatus
    created_by_user_id: str
    updated_by_user_id: str
    created_at: datetime
    updated_at: datetime


class PublishingAttemptResponse(BaseModel):
    id: str
    job_id: str
    attempt_number: int
    status: PublishingJobStatus
    provider_post_id: str | None = None
    error_category: str | None = None
    provider_response_summary: str | None = None
    published_at: datetime | None = None
    created_at: datetime


class PublishingJobResponse(BaseModel):
    id: str
    workspace_id: str
    draft_id: str
    draft_version_id: str
    schedule_id: str | None = None
    platform: PublishingPlatform
    status: PublishingJobStatus
    retry_count: int
    next_retry_at: datetime | None = None
    idempotency_key: str
    error_category: str | None = None
    provider_response_summary: str | None = None
    created_at: datetime
    updated_at: datetime
    attempts: list[PublishingAttemptResponse] = Field(default_factory=list)


class PublishingJobListResponse(BaseModel):
    jobs: list[PublishingJobResponse]


class PublishingProcessRequest(BaseModel):
    limit: int | None = Field(default=None, ge=1, le=10)


class PublishingAuditEventResponse(BaseModel):
    id: str
    workspace_id: str
    user_id: str | None = None
    job_id: str | None = None
    draft_id: str
    draft_version_id: str
    provider: str
    action: str
    attempt_number: int | None = None
    message: str
    created_at: datetime


class PublishingAuditHistoryResponse(BaseModel):
    events: list[PublishingAuditEventResponse]


class WorkspacePublishingSettingsUpdate(BaseModel):
    timezone: str | None = Field(default=None, min_length=1, max_length=80)
    approval_required: bool | None = None
    prevent_self_approval: bool | None = None
    default_platforms: list[PublishingPlatform] | None = Field(default=None, max_length=4)
    max_retry_count: int | None = Field(default=None, ge=0, le=10)
    retry_backoff_base_seconds: int | None = Field(default=None, ge=1, le=3600)
    queue_concurrency: int | None = Field(default=None, ge=1, le=10)
    mock_provider_behavior: MockProviderBehavior | None = None


class WorkspacePublishingSettingsResponse(BaseModel):
    id: str
    workspace_id: str
    timezone: str
    approval_required: bool
    prevent_self_approval: bool
    default_platforms: list[PublishingPlatform]
    max_retry_count: int
    retry_backoff_base_seconds: int
    queue_concurrency: int
    mock_provider_behavior: MockProviderBehavior
    created_at: datetime
    updated_at: datetime
