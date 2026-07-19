import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import BrandRecord, ResearchRecord
from app.schemas.brand import BrandBrain
from app.schemas.research import ResearchRun


@dataclass(frozen=True)
class MigrationResult:
    dry_run: bool
    workspace_id: str
    brands_found: int
    research_runs_found: int
    brands_migrated: int
    research_runs_migrated: int
    backup_paths: list[str]


class JsonMigrationService:
    def __init__(self, db: Session, workspace_id: str) -> None:
        self.db = db
        self.workspace_id = workspace_id

    def migrate(self, dry_run: bool = True) -> MigrationResult:
        brands = self._read_brands()
        research_runs = self._read_research_runs()
        backup_paths = self._backup_paths() if not dry_run else []

        if dry_run:
            return MigrationResult(
                dry_run=True,
                workspace_id=self.workspace_id,
                brands_found=len(brands),
                research_runs_found=len(research_runs),
                brands_migrated=0,
                research_runs_migrated=0,
                backup_paths=[],
            )

        for brand in brands:
            if not self.db.get(BrandRecord, brand.id):
                self.db.add(
                    BrandRecord(
                        id=brand.id,
                        workspace_id=self.workspace_id,
                        payload=brand.model_dump_json(),
                        created_at=brand.created_at,
                        updated_at=brand.updated_at,
                    )
                )
        for run in research_runs:
            if not self.db.get(ResearchRecord, run.id):
                self.db.add(
                    ResearchRecord(
                        id=run.id,
                        workspace_id=self.workspace_id,
                        payload=run.model_dump_json(),
                        created_at=run.created_at,
                        updated_at=run.updated_at,
                    )
                )
        self.db.commit()
        return MigrationResult(
            dry_run=False,
            workspace_id=self.workspace_id,
            brands_found=len(brands),
            research_runs_found=len(research_runs),
            brands_migrated=len(brands),
            research_runs_migrated=len(research_runs),
            backup_paths=backup_paths,
        )

    def _read_brands(self) -> list[BrandBrain]:
        path = Path(settings.brand_store_path)
        if not path.exists():
            return []
        raw = json.loads(path.read_text(encoding="utf-8"))
        return [BrandBrain.model_validate(item) for item in raw.get("brands", [])]

    def _read_research_runs(self) -> list[ResearchRun]:
        path = Path(settings.research_store_path)
        if not path.exists():
            return []
        raw = json.loads(path.read_text(encoding="utf-8"))
        return [ResearchRun.model_validate(item) for item in raw.get("runs", [])]

    def _backup_paths(self) -> list[str]:
        backups = []
        for configured_path in [settings.brand_store_path, settings.research_store_path]:
            path = Path(configured_path)
            if not path.exists():
                continue
            backup = path.with_suffix(f"{path.suffix}.bak")
            shutil.copy2(path, backup)
            backups.append(str(backup))
        return backups
