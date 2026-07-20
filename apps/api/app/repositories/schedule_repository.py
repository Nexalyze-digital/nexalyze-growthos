from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Schedule


class ScheduleRepository:
    def __init__(self, db: Session, workspace_id: str) -> None:
        self.db = db
        self.workspace_id = workspace_id

    def get(self, schedule_id: str) -> Schedule | None:
        schedule = self.db.get(Schedule, schedule_id)
        if not schedule or schedule.workspace_id != self.workspace_id:
            return None
        return schedule

    def active_for_draft(self, draft_id: str) -> Schedule | None:
        return self.db.scalar(
            select(Schedule).where(
                Schedule.workspace_id == self.workspace_id,
                Schedule.draft_id == draft_id,
                Schedule.status == "scheduled",
            )
        )

    def conflict(self, platform: str, scheduled_at_utc: datetime, exclude_schedule_id: str | None = None) -> Schedule | None:
        window_start = scheduled_at_utc - timedelta(minutes=5)
        window_end = scheduled_at_utc + timedelta(minutes=5)
        query = select(Schedule).where(
            Schedule.workspace_id == self.workspace_id,
            Schedule.platform == platform,
            Schedule.status == "scheduled",
            Schedule.scheduled_at_utc >= window_start,
            Schedule.scheduled_at_utc <= window_end,
        )
        if exclude_schedule_id:
            query = query.where(Schedule.id != exclude_schedule_id)
        return self.db.scalar(query)

    def add(self, schedule: Schedule) -> Schedule:
        self.db.add(schedule)
        self.db.flush()
        return schedule
