from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import PublishingAttempt, PublishingJob


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

    def add(self, record: PublishingJob | PublishingAttempt) -> PublishingJob | PublishingAttempt:
        self.db.add(record)
        self.db.flush()
        return record
