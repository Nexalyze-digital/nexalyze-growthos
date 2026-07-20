from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import AuditEvent, BrandRecord, Draft, DraftVersion, ResearchRecord
from app.repositories.draft_repository import DraftRepository
from app.repositories.publishing_utils import encode_hashtags
from app.schemas.auth import WorkspaceRole
from app.schemas.publishing import (
    DraftCreate,
    DraftDuplicateRequest,
    DraftListResponse,
    DraftResponse,
    DraftStatus,
    DraftUpdate,
    DraftVersionListResponse,
    utc_now,
)
from app.services.publishing_serializers import draft_response, version_response


class DraftService:
    def __init__(self, db: Session, workspace_id: str, user_id: str, role: WorkspaceRole) -> None:
        self.db = db
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.role = role
        self.repository = DraftRepository(db, workspace_id)

    def create(self, payload: DraftCreate) -> DraftResponse:
        self._require_editor()
        self._validate_related(payload.brand_id, payload.source_research_run_id)
        now = utc_now()
        draft = Draft(
            workspace_id=self.workspace_id,
            brand_id=payload.brand_id,
            source_research_run_id=payload.source_research_run_id,
            platform=payload.platform.value,
            title=payload.title.strip(),
            body=payload.body.strip(),
            hashtags=encode_hashtags(payload.hashtags),
            status=DraftStatus.generated.value,
            current_version_number=1,
            revision=1,
            created_by_user_id=self.user_id,
            updated_by_user_id=self.user_id,
            created_at=now,
            updated_at=now,
        )
        version = DraftVersion(
            draft_id=draft.id,
            version_number=1,
            title=draft.title,
            body=draft.body,
            hashtags=draft.hashtags,
            created_by_user_id=self.user_id,
            created_at=now,
        )
        self.repository.create(draft, version)
        self._audit("publishing.draft.create", draft.id)
        self.db.commit()
        return draft_response(draft, version)

    def list(self, search: str | None, platform: str | None, status_value: str | None, archived: bool, page: int, page_size: int) -> DraftListResponse:
        drafts, total = self.repository.list(
            search=search,
            platform=platform,
            status=status_value,
            archived=archived,
            page=page,
            page_size=page_size,
        )
        return DraftListResponse(
            drafts=[draft_response(draft, self.repository.latest_version(draft.id)) for draft in drafts],
            page=page,
            page_size=page_size,
            total=total,
        )

    def get(self, draft_id: str) -> DraftResponse:
        draft = self._draft(draft_id)
        return draft_response(draft, self.repository.latest_version(draft.id))

    def update(self, draft_id: str, payload: DraftUpdate) -> DraftResponse:
        self._require_editor()
        draft = self._draft(draft_id)
        if draft.revision != payload.expected_revision:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Draft was modified by another request.")
        if draft.status in {DraftStatus.scheduled.value, DraftStatus.publishing.value, DraftStatus.published.value}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Scheduled or published drafts cannot be edited.")
        self._validate_related(payload.brand_id, payload.source_research_run_id)
        now = utc_now()
        draft.title = payload.title.strip()
        draft.body = payload.body.strip()
        draft.platform = payload.platform.value
        draft.hashtags = encode_hashtags(payload.hashtags)
        draft.brand_id = payload.brand_id
        draft.source_research_run_id = payload.source_research_run_id
        draft.status = DraftStatus.edited.value
        draft.updated_by_user_id = self.user_id
        draft.updated_at = now
        draft.current_version_number += 1
        draft.revision += 1
        version = DraftVersion(
            draft_id=draft.id,
            version_number=draft.current_version_number,
            title=draft.title,
            body=draft.body,
            hashtags=draft.hashtags,
            created_by_user_id=self.user_id,
            created_at=now,
        )
        self.repository.add_version(version)
        self._audit("publishing.draft.update", draft.id)
        self.db.commit()
        return draft_response(draft, version)

    def duplicate(self, draft_id: str, payload: DraftDuplicateRequest) -> DraftResponse:
        self._require_editor()
        source = self._draft(draft_id)
        now = utc_now()
        draft = Draft(
            workspace_id=self.workspace_id,
            brand_id=source.brand_id,
            source_research_run_id=source.source_research_run_id,
            platform=source.platform,
            title=payload.title.strip() if payload.title else f"{source.title} Copy",
            body=source.body,
            hashtags=source.hashtags,
            status=DraftStatus.edited.value,
            current_version_number=1,
            revision=1,
            created_by_user_id=self.user_id,
            updated_by_user_id=self.user_id,
            created_at=now,
            updated_at=now,
        )
        version = DraftVersion(
            draft_id=draft.id,
            version_number=1,
            title=draft.title,
            body=draft.body,
            hashtags=draft.hashtags,
            created_by_user_id=self.user_id,
            created_at=now,
        )
        self.repository.create(draft, version)
        self._audit("publishing.draft.duplicate", draft.id)
        self.db.commit()
        return draft_response(draft, version)

    def archive(self, draft_id: str) -> DraftResponse:
        self._require_editor()
        draft = self._draft(draft_id)
        self.repository.archive(draft)
        self._audit("publishing.draft.archive", draft.id)
        self.db.commit()
        return draft_response(draft, self.repository.latest_version(draft.id))

    def restore(self, draft_id: str) -> DraftResponse:
        self._require_editor()
        draft = self._draft(draft_id)
        if not draft.archived_at:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Draft is not archived.")
        self.repository.restore(draft)
        self._audit("publishing.draft.restore", draft.id)
        self.db.commit()
        return draft_response(draft, self.repository.latest_version(draft.id))

    def versions(self, draft_id: str) -> DraftVersionListResponse:
        draft = self._draft(draft_id)
        return DraftVersionListResponse(versions=[version_response(version) for version in self.repository.versions(draft.id)])

    def _draft(self, draft_id: str) -> Draft:
        draft = self.repository.get(draft_id)
        if not draft:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft was not found.")
        return draft

    def _validate_related(self, brand_id: str | None, research_id: str | None) -> None:
        if brand_id:
            brand = self.db.get(BrandRecord, brand_id)
            if not brand or brand.workspace_id != self.workspace_id:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Brand Brain profile was not found in this workspace.")
        if research_id:
            research = self.db.get(ResearchRecord, research_id)
            if not research or research.workspace_id != self.workspace_id:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Research run was not found in this workspace.")

    def _require_editor(self) -> None:
        if self.role not in {WorkspaceRole.owner, WorkspaceRole.admin, WorkspaceRole.editor}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient workspace permissions.")

    def _audit(self, action: str, target_id: str) -> None:
        self.db.add(AuditEvent(user_id=self.user_id, workspace_id=self.workspace_id, action=action, target_type="draft", target_id=target_id))
