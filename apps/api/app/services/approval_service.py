from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import Approval, ApprovalComment, AuditEvent, WorkspacePublishingSettings
from app.repositories.approval_repository import ApprovalRepository
from app.repositories.draft_repository import DraftRepository
from app.schemas.auth import WorkspaceRole
from app.schemas.publishing import (
    ApprovalResponse,
    ApprovalStatus,
    CommentType,
    DraftStatus,
    ReviewCommentCreate,
    ReviewHistoryResponse,
    utc_now,
)
from app.services.publishing_serializers import approval_response


class ApprovalService:
    def __init__(self, db: Session, workspace_id: str, user_id: str, role: WorkspaceRole) -> None:
        self.db = db
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.role = role
        self.drafts = DraftRepository(db, workspace_id)
        self.approvals = ApprovalRepository(db)

    def submit(self, draft_id: str) -> ApprovalResponse:
        self._require_editor()
        draft = self._draft(draft_id)
        if draft.status not in {DraftStatus.generated.value, DraftStatus.edited.value, DraftStatus.rejected.value}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Draft cannot be submitted from its current state.")
        approval = Approval(
            draft_id=draft.id,
            submitted_by_user_id=self.user_id,
            status=ApprovalStatus.pending.value,
            submitted_at=utc_now(),
        )
        draft.status = DraftStatus.ready_for_review.value
        draft.updated_by_user_id = self.user_id
        draft.updated_at = utc_now()
        self.approvals.add(approval)
        self._audit("publishing.review.submit", draft.id)
        self.db.commit()
        return approval_response(approval, [])

    def approve(self, draft_id: str, payload: ReviewCommentCreate | None = None) -> ApprovalResponse:
        return self._complete_review(draft_id, ApprovalStatus.approved, CommentType.note, payload)

    def reject(self, draft_id: str, payload: ReviewCommentCreate) -> ApprovalResponse:
        return self._complete_review(draft_id, ApprovalStatus.rejected, CommentType.rejection_reason, payload)

    def request_revision(self, draft_id: str, payload: ReviewCommentCreate) -> ApprovalResponse:
        return self._complete_review(draft_id, ApprovalStatus.revision_requested, CommentType.revision_request, payload)

    def add_comment(self, approval_id: str, payload: ReviewCommentCreate) -> ApprovalResponse:
        self._require_editor()
        approval = self.db.get(Approval, approval_id)
        if not approval:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval was not found.")
        draft = self._draft(approval.draft_id)
        comment = ApprovalComment(approval_id=approval.id, user_id=self.user_id, comment_type=CommentType.note.value, body=payload.body.strip())
        self.approvals.add(comment)
        self._audit("publishing.review.comment", draft.id)
        self.db.commit()
        return approval_response(approval, self.approvals.comments_for_approval(approval.id))

    def history(self, draft_id: str) -> ReviewHistoryResponse:
        draft = self._draft(draft_id)
        approvals = self.approvals.list_for_draft(draft.id)
        return ReviewHistoryResponse(
            approvals=[
                approval_response(approval, self.approvals.comments_for_approval(approval.id))
                for approval in approvals
            ]
        )

    def _complete_review(
        self,
        draft_id: str,
        final_status: ApprovalStatus,
        comment_type: CommentType,
        payload: ReviewCommentCreate | None,
    ) -> ApprovalResponse:
        self._require_admin()
        draft = self._draft(draft_id)
        if draft.status != DraftStatus.ready_for_review.value:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Draft is not ready for review.")
        approval = self.approvals.latest_for_draft(draft.id)
        if not approval or approval.status != ApprovalStatus.pending.value:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No pending approval was found.")
        settings = self._settings()
        if settings.prevent_self_approval and approval.submitted_by_user_id == self.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Self-approval is not allowed for this workspace.")
        approval.status = final_status.value
        approval.reviewed_by_user_id = self.user_id
        approval.reviewed_at = utc_now()
        if final_status == ApprovalStatus.approved:
            draft.status = DraftStatus.approved.value
        else:
            draft.status = DraftStatus.rejected.value
        draft.updated_by_user_id = self.user_id
        draft.updated_at = utc_now()
        comments = []
        if payload and payload.body.strip():
            comment = ApprovalComment(approval_id=approval.id, user_id=self.user_id, comment_type=comment_type.value, body=payload.body.strip())
            self.approvals.add(comment)
            comments.append(comment)
        self._audit(f"publishing.review.{final_status.value}", draft.id)
        self.db.commit()
        return approval_response(approval, comments)

    def _settings(self) -> WorkspacePublishingSettings:
        settings = self.db.query(WorkspacePublishingSettings).filter_by(workspace_id=self.workspace_id).one_or_none()
        if settings:
            return settings
        settings = WorkspacePublishingSettings(workspace_id=self.workspace_id)
        self.db.add(settings)
        self.db.flush()
        return settings

    def _draft(self, draft_id: str):
        draft = self.drafts.get(draft_id)
        if not draft:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft was not found.")
        return draft

    def _require_editor(self) -> None:
        if self.role not in {WorkspaceRole.owner, WorkspaceRole.admin, WorkspaceRole.editor}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient workspace permissions.")

    def _require_admin(self) -> None:
        if self.role not in {WorkspaceRole.owner, WorkspaceRole.admin}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient workspace permissions.")

    def _audit(self, action: str, target_id: str) -> None:
        self.db.add(AuditEvent(user_id=self.user_id, workspace_id=self.workspace_id, action=action, target_type="draft", target_id=target_id))
