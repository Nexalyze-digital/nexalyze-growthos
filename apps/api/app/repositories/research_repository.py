from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import ValidationError

from app.schemas.research import ResearchRun


class ResearchRepositoryError(RuntimeError):
    pass


class ResearchRepository:
    def __init__(self, storage_path: str | Path) -> None:
        self.storage_path = Path(storage_path)

    def list(self) -> list[ResearchRun]:
        if not self.storage_path.exists():
            return []
        try:
            raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
            return [ResearchRun.model_validate(item) for item in raw.get("runs", [])]
        except (json.JSONDecodeError, OSError, TypeError, ValidationError) as error:
            raise ResearchRepositoryError("Research storage could not be read safely.") from error

    def get(self, run_id: str) -> ResearchRun | None:
        return next((run for run in self.list() if run.id == run_id), None)

    def create(self, run: ResearchRun) -> ResearchRun:
        runs = self.list()
        runs.insert(0, run)
        self._write(runs)
        return run

    def update(self, run: ResearchRun) -> ResearchRun:
        runs = [existing for existing in self.list() if existing.id != run.id]
        runs.insert(0, run)
        self._write(runs)
        return run

    def delete(self, run_id: str) -> bool:
        runs = self.list()
        remaining = [run for run in runs if run.id != run_id]
        if len(remaining) == len(runs):
            return False
        self._write(remaining)
        return True

    def _write(self, runs: list[ResearchRun]) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"runs": [json.loads(run.model_dump_json()) for run in runs]}
        temporary_path = self.storage_path.with_suffix(f"{self.storage_path.suffix}.tmp")
        temporary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        os.replace(temporary_path, self.storage_path)
