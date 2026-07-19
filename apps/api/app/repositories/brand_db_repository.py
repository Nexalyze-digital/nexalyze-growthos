import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import BrandRecord
from app.repositories.brand_repository import BrandRepositoryError
from app.schemas.brand import BrandBrain


class BrandDbRepository:
    def __init__(self, db: Session, workspace_id: str) -> None:
        self.db = db
        self.workspace_id = workspace_id

    def list(self) -> list[BrandBrain]:
        records = self.db.scalars(
            select(BrandRecord)
            .where(BrandRecord.workspace_id == self.workspace_id)
            .order_by(BrandRecord.updated_at.desc())
        ).all()
        return [self._to_brand(record) for record in records]

    def get(self, brand_id: str) -> BrandBrain | None:
        record = self.db.get(BrandRecord, brand_id)
        if not record or record.workspace_id != self.workspace_id:
            return None
        return self._to_brand(record)

    def get_active(self) -> BrandBrain | None:
        brands = self.list()
        return brands[0] if brands else None

    def create(self, brand: BrandBrain) -> BrandBrain:
        self.db.add(
            BrandRecord(
                id=brand.id,
                workspace_id=self.workspace_id,
                payload=brand.model_dump_json(),
                created_at=brand.created_at,
                updated_at=brand.updated_at,
            )
        )
        self._commit()
        return brand

    def update(self, brand: BrandBrain) -> BrandBrain:
        record = self.db.get(BrandRecord, brand.id)
        if not record or record.workspace_id != self.workspace_id:
            raise BrandRepositoryError("Brand Brain profile was not found.")
        record.payload = brand.model_dump_json()
        record.updated_at = brand.updated_at
        self._commit()
        return brand

    def delete(self, brand_id: str) -> bool:
        record = self.db.get(BrandRecord, brand_id)
        if not record or record.workspace_id != self.workspace_id:
            return False
        self.db.delete(record)
        self._commit()
        return True

    def _to_brand(self, record: BrandRecord) -> BrandBrain:
        try:
            return BrandBrain.model_validate(json.loads(record.payload))
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            raise BrandRepositoryError("Brand Brain storage could not be read safely.") from error

    def _commit(self) -> None:
        try:
            self.db.commit()
        except Exception as error:
            self.db.rollback()
            raise BrandRepositoryError("Brand Brain storage could not be written safely.") from error
