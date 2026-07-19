import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ResearchRecord
from app.repositories.research_repository import ResearchRepositoryError
from app.schemas.research import ResearchRun


class ResearchDbRepository:
    def __init__(self, db: Session, workspace_id: str) -> None:
        self.db = db
        self.workspace_id = workspace_id

    def list(self) -> list[ResearchRun]:
        records = self.db.scalars(
            select(ResearchRecord)
            .where(ResearchRecord.workspace_id == self.workspace_id)
            .order_by(ResearchRecord.updated_at.desc())
        ).all()
        return [self._to_run(record) for record in records]

    def get(self, run_id: str) -> ResearchRun | None:
        record = self.db.get(ResearchRecord, run_id)
        if not record or record.workspace_id != self.workspace_id:
            return None
        return self._to_run(record)

    def create(self, run: ResearchRun) -> ResearchRun:
        self.db.add(
            ResearchRecord(
                id=run.id,
                workspace_id=self.workspace_id,
                payload=run.model_dump_json(),
                created_at=run.created_at,
                updated_at=run.updated_at,
            )
        )
        self._commit()
        return run

    def update(self, run: ResearchRun) -> ResearchRun:
        record = self.db.get(ResearchRecord, run.id)
        if not record or record.workspace_id != self.workspace_id:
            raise ResearchRepositoryError("Research run was not found.")
        record.payload = run.model_dump_json()
        record.updated_at = run.updated_at
        self._commit()
        return run

    def delete(self, run_id: str) -> bool:
        record = self.db.get(ResearchRecord, run_id)
        if not record or record.workspace_id != self.workspace_id:
            return False
        self.db.delete(record)
        self._commit()
        return True

    def _to_run(self, record: ResearchRecord) -> ResearchRun:
        try:
            return ResearchRun.model_validate(json.loads(record.payload))
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            raise ResearchRepositoryError("Research storage could not be read safely.") from error

    def _commit(self) -> None:
        try:
            self.db.commit()
        except Exception as error:
            self.db.rollback()
            raise ResearchRepositoryError("Research storage could not be written safely.") from error
