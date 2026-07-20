from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import AuditEvent, Draft, PublishingAttempt, PublishingAuditEvent, PublishingJob, WorkspacePublishingSettings
from app.providers.publishing import MockPublishingProvider
from app.repositories.draft_repository import DraftRepository
from app.repositories.publishing_repository import PublishingRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.schemas.auth import WorkspaceRole
from app.schemas.publishing import (
    DraftStatus,
    PublishingAuditHistoryResponse,
    PublishingJobListResponse,
    PublishingJobResponse,
    PublishingJobStatus,
    WorkspacePublishingSettingsResponse,
    WorkspacePublishingSettingsUpdate,
    utc_now,
)
from app.services.publishing_serializers import job_response, publishing_audit_response, publishing_settings_response


class PublishingQueueService:
    def __init__(self, db: Session, workspace_id: str, user_id: str, role: WorkspaceRole) -> None:
        self.db = db
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.role = role
        self.drafts = DraftRepository(db, workspace_id)
        self.schedules = ScheduleRepository(db, workspace_id)
        self.jobs = PublishingRepository(db, workspace_id)
        self.provider = MockPublishingProvider()

    def enqueue(self, draft_id: str) -> PublishingJobResponse:
        self._require_admin()
        draft = self.drafts.get(draft_id)
        if not draft:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft was not found.")
        if draft.status not in {DraftStatus.approved.value, DraftStatus.scheduled.value}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only approved or scheduled drafts can be enqueued.")
        latest = self.drafts.latest_version(draft.id)
        schedule = self.schedules.active_for_draft(draft.id)
        version_id = schedule.draft_version_id if schedule else latest.id
        scheduled_marker = schedule.scheduled_at_utc.isoformat() if schedule else "manual"
        key = f"{self.workspace_id}:{draft.id}:{draft.platform}:{scheduled_marker}:{version_id}"
        existing = self.jobs.by_idempotency_key(key)
        if existing:
            return job_response(existing, self.jobs.attempts(existing.id))
        job = PublishingJob(
            workspace_id=self.workspace_id,
            draft_id=draft.id,
            draft_version_id=version_id,
            schedule_id=schedule.id if schedule else None,
            platform=draft.platform,
            status=PublishingJobStatus.pending.value,
            retry_count=0,
            idempotency_key=key,
        )
        self.jobs.add(job)
        self._general_audit("publishing.queue.enqueue", draft.id)
        self._publishing_audit(job, "created", None, "Publishing job created.")
        self._publishing_audit(job, "queued", None, "Publishing job queued for deterministic mock delivery.")
        self.db.commit()
        return job_response(job, [])

    def list(self) -> PublishingJobListResponse:
        return PublishingJobListResponse(jobs=[job_response(job, self.jobs.attempts(job.id)) for job in self.jobs.list()])

    def get(self, job_id: str) -> PublishingJobResponse:
        job = self._job(job_id)
        return job_response(job, self.jobs.attempts(job.id))

    def process_next(self, limit: int | None = None) -> PublishingJobListResponse:
        self._require_admin()
        settings = self._settings()
        jobs = self.jobs.next_processable(min(limit or settings.queue_concurrency, settings.queue_concurrency), utc_now())
        processed = [self._process(job, settings) for job in jobs]
        self.db.commit()
        return PublishingJobListResponse(jobs=[job_response(job, self.jobs.attempts(job.id)) for job in processed])

    def process(self, job_id: str) -> PublishingJobResponse:
        self._require_admin()
        job = self._job(job_id)
        if job.status not in {PublishingJobStatus.pending.value, PublishingJobStatus.retry_pending.value}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only pending jobs can be processed.")
        if job.next_retry_at and self._as_utc(job.next_retry_at) > utc_now():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Job is waiting for its retry window.")
        processed = self._process(job, self._settings())
        self.db.commit()
        return job_response(processed, self.jobs.attempts(processed.id))

    def retry(self, job_id: str) -> PublishingJobResponse:
        self._require_admin()
        job = self._job(job_id)
        if job.status not in {PublishingJobStatus.failed.value, PublishingJobStatus.retry_pending.value, PublishingJobStatus.dead_letter.value}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only failed or retry-pending jobs can be retried.")
        if job.error_category not in {"transient", "manual_retry"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only retryable jobs can be retried.")
        settings = self._settings()
        if job.retry_count >= settings.max_retry_count:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Job has reached the maximum retry count.")
        job.status = PublishingJobStatus.retry_pending.value
        job.retry_count += 1
        job.next_retry_at = utc_now()
        job.updated_at = utc_now()
        attempt = PublishingAttempt(
            job_id=job.id,
            attempt_number=len(self.jobs.attempts(job.id)) + 1,
            status=PublishingJobStatus.pending.value,
            provider_response_summary="Retry queued by GrowthOS mock publishing foundation.",
        )
        self.jobs.add(attempt)
        self._publishing_audit(job, "retry_pending", attempt.attempt_number, "Retry queued by a workspace admin.")
        self._general_audit("publishing.queue.retry", job.draft_id)
        self.db.commit()
        return job_response(job, self.jobs.attempts(job.id))

    def cancel(self, job_id: str) -> PublishingJobResponse:
        self._require_admin()
        job = self._job(job_id)
        if job.status not in {
            PublishingJobStatus.pending.value,
            PublishingJobStatus.retry_pending.value,
            PublishingJobStatus.failed.value,
            PublishingJobStatus.dead_letter.value,
        }:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only pending, retry-pending, failed, or dead-letter jobs can be cancelled.")
        job.status = PublishingJobStatus.cancelled.value
        job.updated_at = utc_now()
        self._publishing_audit(job, "cancelled", None, "Publishing job cancelled by a workspace admin.")
        self._general_audit("publishing.queue.cancel", job.draft_id)
        self.db.commit()
        return job_response(job, self.jobs.attempts(job.id))

    def audit_history(self, job_id: str) -> PublishingAuditHistoryResponse:
        self._job(job_id)
        return PublishingAuditHistoryResponse(events=[publishing_audit_response(event) for event in self.jobs.audit_events(job_id)])

    def get_settings(self) -> WorkspacePublishingSettingsResponse:
        return publishing_settings_response(self._settings())

    def update_settings(self, payload: WorkspacePublishingSettingsUpdate) -> WorkspacePublishingSettingsResponse:
        self._require_owner()
        settings = self._settings()
        if payload.timezone is not None:
            settings.timezone = payload.timezone
        if payload.approval_required is not None:
            settings.approval_required = payload.approval_required
        if payload.prevent_self_approval is not None:
            settings.prevent_self_approval = payload.prevent_self_approval
        if payload.default_platforms is not None:
            settings.default_platforms = json.dumps([platform.value for platform in payload.default_platforms])
        if payload.max_retry_count is not None:
            settings.max_retry_count = payload.max_retry_count
        if payload.retry_backoff_base_seconds is not None:
            settings.retry_backoff_base_seconds = payload.retry_backoff_base_seconds
        if payload.queue_concurrency is not None:
            settings.queue_concurrency = payload.queue_concurrency
        if payload.mock_provider_behavior is not None:
            settings.mock_provider_behavior = payload.mock_provider_behavior.value
        settings.updated_at = utc_now()
        self._general_audit("publishing.settings.update", settings.id)
        self.db.commit()
        return publishing_settings_response(settings)

    def _process(self, job: PublishingJob, settings: WorkspacePublishingSettings) -> PublishingJob:
        draft = self.drafts.get(job.draft_id)
        if not draft:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Job draft is no longer available.")
        attempts = self.jobs.attempts(job.id)
        attempt_number = len(attempts) + 1
        job.status = PublishingJobStatus.processing.value
        job.updated_at = utc_now()
        attempt = PublishingAttempt(
            job_id=job.id,
            attempt_number=attempt_number,
            status=PublishingJobStatus.processing.value,
            provider_response_summary="Deterministic mock publishing attempt started.",
        )
        self.jobs.add(attempt)
        self._publishing_audit(job, "processing", attempt_number, "Publishing job locked for processing.")
        result = self.provider.publish(job, draft, attempt_number, settings.mock_provider_behavior)
        attempt.provider_post_id = result.provider_post_id
        attempt.error_category = result.error_category
        attempt.provider_response_summary = result.summary
        attempt.published_at = result.published_at
        job.error_category = result.error_category
        job.provider_response_summary = result.summary
        job.next_retry_at = None
        if result.status == PublishingJobStatus.published:
            self._mark_published(job, draft, attempt, result.published_at)
        elif result.error_category == "transient":
            self._mark_transient_failure(job, attempt, settings)
        else:
            self._mark_dead_letter(job, attempt, "Permanent provider rejection.")
        job.updated_at = utc_now()
        return job

    def _mark_published(self, job: PublishingJob, draft: Draft, attempt: PublishingAttempt, published_at) -> None:
        job.status = PublishingJobStatus.published.value
        attempt.status = PublishingJobStatus.published.value
        draft.status = DraftStatus.published.value
        draft.updated_at = utc_now()
        if job.schedule_id:
            schedule = self.schedules.get(job.schedule_id)
            if schedule:
                schedule.status = "published"
                schedule.updated_at = utc_now()
        self._publishing_audit(job, "published", attempt.attempt_number, f"Mock provider published post {attempt.provider_post_id}.")
        self._general_audit("publishing.queue.published", job.draft_id)

    def _mark_transient_failure(self, job: PublishingJob, attempt: PublishingAttempt, settings: WorkspacePublishingSettings) -> None:
        attempt.status = PublishingJobStatus.failed.value
        if job.retry_count >= settings.max_retry_count:
            self._mark_dead_letter(job, attempt, "Retry budget exhausted after transient provider errors.")
            return
        job.retry_count += 1
        job.status = PublishingJobStatus.retry_pending.value
        job.next_retry_at = utc_now() + timedelta(seconds=settings.retry_backoff_base_seconds * (2 ** (job.retry_count - 1)))
        self._publishing_audit(job, "failed", attempt.attempt_number, "Transient provider error recorded.")
        self._publishing_audit(job, "retry_pending", attempt.attempt_number, "Automatic retry scheduled with exponential backoff.")

    def _mark_dead_letter(self, job: PublishingJob, attempt: PublishingAttempt, message: str) -> None:
        job.status = PublishingJobStatus.dead_letter.value
        attempt.status = PublishingJobStatus.failed.value
        self._publishing_audit(job, "failed", attempt.attempt_number, attempt.provider_response_summary or message)
        self._publishing_audit(job, "dead_letter", attempt.attempt_number, message)

    def _job(self, job_id: str) -> PublishingJob:
        job = self.jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publishing job was not found.")
        return job

    def _require_admin(self) -> None:
        if self.role not in {WorkspaceRole.owner, WorkspaceRole.admin}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient workspace permissions.")

    def _require_owner(self) -> None:
        if self.role != WorkspaceRole.owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only workspace owners can update publishing settings.")

    def _settings(self) -> WorkspacePublishingSettings:
        settings = self.jobs.settings()
        if settings:
            return settings
        settings = WorkspacePublishingSettings(workspace_id=self.workspace_id)
        return self.jobs.add(settings)

    def _general_audit(self, action: str, target_id: str) -> None:
        self.db.add(AuditEvent(user_id=self.user_id, workspace_id=self.workspace_id, action=action, target_type="publishing_job", target_id=target_id))

    def _publishing_audit(self, job: PublishingJob, action: str, attempt_number: int | None, message: str) -> None:
        self.jobs.add(
            PublishingAuditEvent(
                workspace_id=self.workspace_id,
                user_id=self.user_id,
                job_id=job.id,
                draft_id=job.draft_id,
                draft_version_id=job.draft_version_id,
                provider=self.provider.name,
                action=action,
                attempt_number=attempt_number,
                message=message,
            )
        )

    def _as_utc(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
