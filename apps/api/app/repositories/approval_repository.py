from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Approval, ApprovalComment


class ApprovalRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def latest_for_draft(self, draft_id: str) -> Approval | None:
        return self.db.scalar(
            select(Approval).where(Approval.draft_id == draft_id).order_by(Approval.submitted_at.desc())
        )

    def list_for_draft(self, draft_id: str) -> list[Approval]:
        return list(
            self.db.scalars(
                select(Approval).where(Approval.draft_id == draft_id).order_by(Approval.submitted_at.desc())
            ).all()
        )

    def comments_for_approval(self, approval_id: str) -> list[ApprovalComment]:
        return list(
            self.db.scalars(
                select(ApprovalComment)
                .where(ApprovalComment.approval_id == approval_id)
                .order_by(ApprovalComment.created_at.asc())
            ).all()
        )

    def add(self, record: Approval | ApprovalComment) -> Approval | ApprovalComment:
        self.db.add(record)
        self.db.flush()
        return record
