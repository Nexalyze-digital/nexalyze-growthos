import json

from app.db.models import Approval, ApprovalComment, Draft, DraftVersion, PublishingAttempt, PublishingAuditEvent, PublishingJob, Schedule, WorkspacePublishingSettings
from app.repositories.publishing_utils import decode_hashtags
from app.schemas.publishing import (
    ApprovalCommentResponse,
    ApprovalResponse,
    DraftResponse,
    DraftVersionResponse,
    PublishingAttemptResponse,
    PublishingJobResponse,
    PublishingAuditEventResponse,
    ScheduleResponse,
    WorkspacePublishingSettingsResponse,
)


def version_response(version: DraftVersion) -> DraftVersionResponse:
    return DraftVersionResponse(
        id=version.id,
        draft_id=version.draft_id,
        version_number=version.version_number,
        title=version.title,
        body=version.body,
        hashtags=decode_hashtags(version.hashtags),
        created_by_user_id=version.created_by_user_id,
        created_at=version.created_at,
    )


def draft_response(draft: Draft, latest_version: DraftVersion | None = None) -> DraftResponse:
    return DraftResponse(
        id=draft.id,
        workspace_id=draft.workspace_id,
        brand_id=draft.brand_id,
        source_research_run_id=draft.source_research_run_id,
        platform=draft.platform,
        title=draft.title,
        body=draft.body,
        hashtags=decode_hashtags(draft.hashtags),
        status=draft.status,
        current_version_number=draft.current_version_number,
        revision=draft.revision,
        created_by_user_id=draft.created_by_user_id,
        updated_by_user_id=draft.updated_by_user_id,
        archived_at=draft.archived_at,
        created_at=draft.created_at,
        updated_at=draft.updated_at,
        latest_version=version_response(latest_version) if latest_version else None,
    )


def comment_response(comment: ApprovalComment) -> ApprovalCommentResponse:
    return ApprovalCommentResponse(
        id=comment.id,
        approval_id=comment.approval_id,
        user_id=comment.user_id,
        comment_type=comment.comment_type,
        body=comment.body,
        created_at=comment.created_at,
    )


def approval_response(approval: Approval, comments: list[ApprovalComment]) -> ApprovalResponse:
    return ApprovalResponse(
        id=approval.id,
        draft_id=approval.draft_id,
        submitted_by_user_id=approval.submitted_by_user_id,
        reviewed_by_user_id=approval.reviewed_by_user_id,
        status=approval.status,
        submitted_at=approval.submitted_at,
        reviewed_at=approval.reviewed_at,
        comments=[comment_response(comment) for comment in comments],
    )


def schedule_response(schedule: Schedule) -> ScheduleResponse:
    return ScheduleResponse(
        id=schedule.id,
        draft_id=schedule.draft_id,
        draft_version_id=schedule.draft_version_id,
        workspace_id=schedule.workspace_id,
        platform=schedule.platform,
        scheduled_at_utc=schedule.scheduled_at_utc,
        workspace_timezone=schedule.workspace_timezone,
        status=schedule.status,
        created_by_user_id=schedule.created_by_user_id,
        updated_by_user_id=schedule.updated_by_user_id,
        created_at=schedule.created_at,
        updated_at=schedule.updated_at,
    )


def attempt_response(attempt: PublishingAttempt) -> PublishingAttemptResponse:
    return PublishingAttemptResponse(
        id=attempt.id,
        job_id=attempt.job_id,
        attempt_number=attempt.attempt_number,
        status=attempt.status,
        provider_post_id=attempt.provider_post_id,
        error_category=attempt.error_category,
        provider_response_summary=attempt.provider_response_summary,
        published_at=attempt.published_at,
        created_at=attempt.created_at,
    )


def job_response(job: PublishingJob, attempts: list[PublishingAttempt]) -> PublishingJobResponse:
    return PublishingJobResponse(
        id=job.id,
        workspace_id=job.workspace_id,
        draft_id=job.draft_id,
        draft_version_id=job.draft_version_id,
        schedule_id=job.schedule_id,
        platform=job.platform,
        status=job.status,
        retry_count=job.retry_count,
        next_retry_at=job.next_retry_at,
        idempotency_key=job.idempotency_key,
        error_category=job.error_category,
        provider_response_summary=job.provider_response_summary,
        created_at=job.created_at,
        updated_at=job.updated_at,
        attempts=[attempt_response(attempt) for attempt in attempts],
    )


def publishing_audit_response(event: PublishingAuditEvent) -> PublishingAuditEventResponse:
    return PublishingAuditEventResponse(
        id=event.id,
        workspace_id=event.workspace_id,
        user_id=event.user_id,
        job_id=event.job_id,
        draft_id=event.draft_id,
        draft_version_id=event.draft_version_id,
        provider=event.provider,
        action=event.action,
        attempt_number=event.attempt_number,
        message=event.message,
        created_at=event.created_at,
    )


def publishing_settings_response(settings: WorkspacePublishingSettings) -> WorkspacePublishingSettingsResponse:
    try:
        platforms = json.loads(settings.default_platforms or "[]")
    except json.JSONDecodeError:
        platforms = []
    return WorkspacePublishingSettingsResponse(
        id=settings.id,
        workspace_id=settings.workspace_id,
        timezone=settings.timezone,
        approval_required=settings.approval_required,
        prevent_self_approval=settings.prevent_self_approval,
        default_platforms=platforms,
        max_retry_count=settings.max_retry_count,
        retry_backoff_base_seconds=settings.retry_backoff_base_seconds,
        queue_concurrency=settings.queue_concurrency,
        mock_provider_behavior=settings.mock_provider_behavior,
        created_at=settings.created_at,
        updated_at=settings.updated_at,
    )
