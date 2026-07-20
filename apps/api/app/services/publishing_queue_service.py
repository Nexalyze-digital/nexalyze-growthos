from __future__ import annotations

from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import AuditEvent, PublishingAttempt, PublishingJob
from app.repositories.draft_repository import DraftRepository
from app.repositories.publishing_repository import PublishingRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.schemas.auth import WorkspaceRole
from app.schemas.publishing import DraftStatus, PublishingJobListResponse, PublishingJobResponse, PublishingJobStatus, utc_now
from app.services.publishing_serializers import job_response


class PublishingQueueService:
    def __init__(self, db: Session, workspace_id: str, user_id: str, role: WorkspaceRole) -> None:
        self.db = db
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.role = role
        self.drafts = DraftRepository(db, workspace_id)
        self.schedules = ScheduleRepository(db, workspace_id)
        self.jobs = PublishingRepository(db, workspace_id)

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
        self._audit("publishing.queue.enqueue", draft.id)
        self.db.commit()
        return job_response(job, [])

    def list(self) -> PublishingJobListResponse:
        return PublishingJobListResponse(jobs=[job_response(job, self.jobs.attempts(job.id)) for job in self.jobs.list()])

    def get(self, job_id: str) -> PublishingJobResponse:
        job = self._job(job_id)
        return job_response(job, self.jobs.attempts(job.id))

    def retry(self, job_id: str) -> PublishingJobResponse:
        self._require_admin()
        job = self._job(job_id)
        if job.status != PublishingJobStatus.failed.value or job.error_category != "transient":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only transient failed jobs can be retried.")
        job.status = PublishingJobStatus.pending.value
        job.retry_count += 1
        job.next_retry_at = utc_now() + timedelta(minutes=min(30, 2**job.retry_count))
        job.updated_at = utc_now()
        attempt = PublishingAttempt(
            job_id=job.id,
            attempt_number=len(self.jobs.attempts(job.id)) + 1,
            status=PublishingJobStatus.pending.value,
            provider_response_summary="Retry queued by GrowthOS mock publishing foundation.",
        )
        self.jobs.add(attempt)
        self._audit("publishing.queue.retry", job.draft_id)
        self.db.commit()
        return job_response(job, self.jobs.attempts(job.id))

    def cancel(self, job_id: str) -> PublishingJobResponse:
        self._require_admin()
        job = self._job(job_id)
        if job.status not in {PublishingJobStatus.pending.value, PublishingJobStatus.failed.value}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only pending or failed jobs can be cancelled.")
        job.status = PublishingJobStatus.cancelled.value
        job.updated_at = utc_now()
        self._audit("publishing.queue.cancel", job.draft_id)
        self.db.commit()
        return job_response(job, self.jobs.attempts(job.id))

    def _job(self, job_id: str) -> PublishingJob:
        job = self.jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publishing job was not found.")
        return job

    def _require_admin(self) -> None:
        if self.role not in {WorkspaceRole.owner, WorkspaceRole.admin}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient workspace permissions.")

    def _audit(self, action: str, target_id: str) -> None:
        self.db.add(AuditEvent(user_id=self.user_id, workspace_id=self.workspace_id, action=action, target_type="publishing_job", target_id=target_id))
