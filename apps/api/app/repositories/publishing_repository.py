from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import PublishingAttempt, PublishingAuditEvent, PublishingJob, WorkspacePublishingSettings


class PublishingRepository:
    def __init__(self, db: Session, workspace_id: str) -> None:
        self.db = db
        self.workspace_id = workspace_id

    def get(self, job_id: str) -> PublishingJob | None:
        job = self.db.get(PublishingJob, job_id)
        if not job or job.workspace_id != self.workspace_id:
            return None
        return job

    def list(self) -> list[PublishingJob]:
        return list(
            self.db.scalars(
                select(PublishingJob)
                .where(PublishingJob.workspace_id == self.workspace_id)
                .order_by(PublishingJob.updated_at.desc())
            ).all()
        )

    def next_processable(self, limit: int, now: datetime) -> list[PublishingJob]:
        return list(
            self.db.scalars(
                select(PublishingJob)
                .where(
                    PublishingJob.workspace_id == self.workspace_id,
                    PublishingJob.status.in_(("pending", "retry_pending")),
                    (PublishingJob.next_retry_at.is_(None)) | (PublishingJob.next_retry_at <= now),
                )
                .order_by(PublishingJob.created_at.asc())
                .limit(limit)
            ).all()
        )

    def by_idempotency_key(self, key: str) -> PublishingJob | None:
        return self.db.scalar(
            select(PublishingJob).where(
                PublishingJob.workspace_id == self.workspace_id,
                PublishingJob.idempotency_key == key,
            )
        )

    def attempts(self, job_id: str) -> list[PublishingAttempt]:
        return list(
            self.db.scalars(
                select(PublishingAttempt)
                .where(PublishingAttempt.job_id == job_id)
                .order_by(PublishingAttempt.attempt_number.asc())
            ).all()
        )

    def audit_events(self, job_id: str) -> list[PublishingAuditEvent]:
        return list(
            self.db.scalars(
                select(PublishingAuditEvent)
                .where(
                    PublishingAuditEvent.workspace_id == self.workspace_id,
                    PublishingAuditEvent.job_id == job_id,
                )
                .order_by(PublishingAuditEvent.created_at.asc())
            ).all()
        )

    def settings(self) -> WorkspacePublishingSettings | None:
        return self.db.scalar(select(WorkspacePublishingSettings).where(WorkspacePublishingSettings.workspace_id == self.workspace_id))

    def add(
        self,
        record: PublishingJob | PublishingAttempt | PublishingAuditEvent | WorkspacePublishingSettings,
    ) -> PublishingJob | PublishingAttempt | PublishingAuditEvent | WorkspacePublishingSettings:
        self.db.add(record)
        self.db.flush()
        return record
