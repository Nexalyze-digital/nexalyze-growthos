from __future__ import annotations

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.db.models import Draft, DraftVersion
from app.schemas.publishing import DraftStatus, utc_now


class DraftRepository:
    def __init__(self, db: Session, workspace_id: str) -> None:
        self.db = db
        self.workspace_id = workspace_id

    def create(self, draft: Draft, version: DraftVersion) -> Draft:
        self.db.add(draft)
        self.db.flush()
        version.draft_id = draft.id
        self.db.add(version)
        self.db.flush()
        return draft

    def list(
        self,
        *,
        search: str | None = None,
        platform: str | None = None,
        status: str | None = None,
        archived: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Draft], int]:
        query = select(Draft).where(Draft.workspace_id == self.workspace_id, Draft.deleted_at.is_(None))
        query = self._apply_filters(query, search=search, platform=platform, status=status, archived=archived)
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        drafts = self.db.scalars(
            query.order_by(Draft.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
        ).all()
        return list(drafts), total

    def get(self, draft_id: str, include_deleted: bool = False) -> Draft | None:
        draft = self.db.get(Draft, draft_id)
        if not draft or draft.workspace_id != self.workspace_id:
            return None
        if draft.deleted_at and not include_deleted:
            return None
        return draft

    def latest_version(self, draft_id: str) -> DraftVersion | None:
        return self.db.scalar(
            select(DraftVersion)
            .where(DraftVersion.draft_id == draft_id)
            .order_by(DraftVersion.version_number.desc())
        )

    def versions(self, draft_id: str) -> list[DraftVersion]:
        return list(
            self.db.scalars(
                select(DraftVersion)
                .where(DraftVersion.draft_id == draft_id)
                .order_by(DraftVersion.version_number.desc())
            ).all()
        )

    def add_version(self, version: DraftVersion) -> DraftVersion:
        self.db.add(version)
        self.db.flush()
        return version

    def save(self) -> None:
        self.db.flush()

    def archive(self, draft: Draft) -> None:
        now = utc_now()
        draft.status = DraftStatus.archived.value
        draft.archived_at = now
        draft.updated_at = now
        self.db.flush()

    def restore(self, draft: Draft) -> None:
        draft.status = DraftStatus.edited.value
        draft.archived_at = None
        draft.updated_at = utc_now()
        self.db.flush()

    def _apply_filters(
        self,
        query: Select[tuple[Draft]],
        *,
        search: str | None,
        platform: str | None,
        status: str | None,
        archived: bool,
    ) -> Select[tuple[Draft]]:
        if archived:
            query = query.where(Draft.archived_at.is_not(None))
        else:
            query = query.where(Draft.archived_at.is_(None))
        if search:
            pattern = f"%{search.strip()}%"
            query = query.where(or_(Draft.title.ilike(pattern), Draft.body.ilike(pattern)))
        if platform:
            query = query.where(Draft.platform == platform)
        if status:
            query = query.where(Draft.status == status)
        return query
