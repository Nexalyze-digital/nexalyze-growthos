from __future__ import annotations

import json
from pathlib import Path

from app.schemas.brand import BrandBrain


class BrandRepository:
    def __init__(self, storage_path: str | Path) -> None:
        self.storage_path = Path(storage_path)

    def list(self) -> list[BrandBrain]:
        if not self.storage_path.exists():
            return []

        raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
        return [BrandBrain.model_validate(item) for item in raw.get("brands", [])]

    def get(self, brand_id: str) -> BrandBrain | None:
        return next((brand for brand in self.list() if brand.id == brand_id), None)

    def get_active(self) -> BrandBrain | None:
        brands = self.list()
        return brands[0] if brands else None

    def create(self, brand: BrandBrain) -> BrandBrain:
        brands = self.list()
        brands.append(brand)
        self._write(brands)
        return brand

    def update(self, brand: BrandBrain) -> BrandBrain:
        brands = [existing for existing in self.list() if existing.id != brand.id]
        brands.insert(0, brand)
        self._write(brands)
        return brand

    def delete(self, brand_id: str) -> bool:
        brands = self.list()
        remaining = [brand for brand in brands if brand.id != brand_id]
        if len(remaining) == len(brands):
            return False
        self._write(remaining)
        return True

    def _write(self, brands: list[BrandBrain]) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "brands": [
                json.loads(brand.model_dump_json()) for brand in brands
            ]
        }
        self.storage_path.write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )
