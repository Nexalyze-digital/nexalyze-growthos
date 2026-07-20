from datetime import timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import AuditEvent, Schedule
from app.repositories.draft_repository import DraftRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.schemas.auth import WorkspaceRole
from app.schemas.publishing import DraftStatus, ScheduleCreate, ScheduleResponse, ScheduleStatus, ScheduleUpdate, utc_now
from app.services.publishing_serializers import schedule_response


class ScheduleService:
    def __init__(self, db: Session, workspace_id: str, user_id: str, role: WorkspaceRole) -> None:
        self.db = db
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.role = role
        self.drafts = DraftRepository(db, workspace_id)
        self.schedules = ScheduleRepository(db, workspace_id)

    def schedule(self, draft_id: str, payload: ScheduleCreate) -> ScheduleResponse:
        self._require_admin()
        draft = self._approved_draft(draft_id)
        if self.schedules.active_for_draft(draft.id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Draft is already scheduled.")
        scheduled_at_utc = self._to_utc(payload.scheduled_at, payload.timezone)
        if self.schedules.conflict(draft.platform, scheduled_at_utc):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Another draft is already scheduled for this platform and time window.")
        latest = self.drafts.latest_version(draft.id)
        schedule = Schedule(
            draft_id=draft.id,
            draft_version_id=latest.id,
            workspace_id=self.workspace_id,
            platform=draft.platform,
            scheduled_at_utc=scheduled_at_utc,
            workspace_timezone=payload.timezone,
            status=ScheduleStatus.scheduled.value,
            created_by_user_id=self.user_id,
            updated_by_user_id=self.user_id,
        )
        draft.status = DraftStatus.scheduled.value
        draft.updated_by_user_id = self.user_id
        draft.updated_at = utc_now()
        self.schedules.add(schedule)
        self._audit("publishing.schedule.create", draft.id)
        self.db.commit()
        return schedule_response(schedule)

    def reschedule(self, schedule_id: str, payload: ScheduleUpdate) -> ScheduleResponse:
        self._require_admin()
        schedule = self._schedule(schedule_id)
        if schedule.status != ScheduleStatus.scheduled.value:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only scheduled items can be rescheduled.")
        scheduled_at_utc = self._to_utc(payload.scheduled_at, payload.timezone)
        if self.schedules.conflict(schedule.platform, scheduled_at_utc, exclude_schedule_id=schedule.id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Another draft is already scheduled for this platform and time window.")
        schedule.scheduled_at_utc = scheduled_at_utc
        schedule.workspace_timezone = payload.timezone
        schedule.updated_by_user_id = self.user_id
        schedule.updated_at = utc_now()
        self._audit("publishing.schedule.update", schedule.draft_id)
        self.db.commit()
        return schedule_response(schedule)

    def unschedule(self, schedule_id: str) -> ScheduleResponse:
        self._require_admin()
        schedule = self._schedule(schedule_id)
        if schedule.status != ScheduleStatus.scheduled.value:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only scheduled items can be unscheduled.")
        draft = self.drafts.get(schedule.draft_id)
        schedule.status = ScheduleStatus.unscheduled.value
        schedule.updated_by_user_id = self.user_id
        schedule.updated_at = utc_now()
        if draft:
            draft.status = DraftStatus.approved.value
            draft.updated_at = utc_now()
            draft.updated_by_user_id = self.user_id
        self._audit("publishing.schedule.unschedule", schedule.draft_id)
        self.db.commit()
        return schedule_response(schedule)

    def _to_utc(self, value, timezone_name: str):
        try:
            zone = ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError as error:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Invalid timezone.") from error
        local = value.replace(tzinfo=zone) if value.tzinfo is None else value.astimezone(zone)
        scheduled_at_utc = local.astimezone(timezone.utc)
        if scheduled_at_utc <= utc_now():
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Schedule time must be in the future.")
        return scheduled_at_utc

    def _approved_draft(self, draft_id: str):
        draft = self.drafts.get(draft_id)
        if not draft:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft was not found.")
        if draft.status != DraftStatus.approved.value:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only approved drafts can be scheduled.")
        return draft

    def _schedule(self, schedule_id: str) -> Schedule:
        schedule = self.schedules.get(schedule_id)
        if not schedule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule was not found.")
        return schedule

    def _require_admin(self) -> None:
        if self.role not in {WorkspaceRole.owner, WorkspaceRole.admin}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient workspace permissions.")

    def _audit(self, action: str, target_id: str) -> None:
        self.db.add(AuditEvent(user_id=self.user_id, workspace_id=self.workspace_id, action=action, target_type="schedule", target_id=target_id))
