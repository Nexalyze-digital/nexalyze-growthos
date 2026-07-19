from pathlib import Path

from fastapi import HTTPException, status

from app.core.config import settings
from app.repositories.brand_repository import BrandRepository, BrandRepositoryError
from app.schemas.brand import (
    BrandBrain,
    BrandBrainCreate,
    BrandBrainUpdate,
    BrandContextSummary,
    utc_now,
)


class BrandService:
    def __init__(self, repository: BrandRepository) -> None:
        self.repository = repository

    def list_brands(self) -> list[BrandBrain]:
        return self._read(lambda: self.repository.list())

    def get_brand(self, brand_id: str) -> BrandBrain:
        brand = self._read(lambda: self.repository.get(brand_id))
        if brand is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand Brain profile was not found.",
            )
        return brand

    def create_brand(self, payload: BrandBrainCreate) -> BrandBrain:
        try:
            return self.repository.create(BrandBrain(**payload.model_dump()))
        except BrandRepositoryError as error:
            raise self._storage_error() from error

    def update_brand(self, brand_id: str, payload: BrandBrainUpdate) -> BrandBrain:
        existing = self.get_brand(brand_id)
        updated = BrandBrain(
            **payload.model_dump(),
            id=existing.id,
            created_at=existing.created_at,
            updated_at=utc_now(),
        )
        try:
            return self.repository.update(updated)
        except BrandRepositoryError as error:
            raise self._storage_error() from error

    def delete_brand(self, brand_id: str) -> None:
        try:
            deleted = self.repository.delete(brand_id)
        except BrandRepositoryError as error:
            raise self._storage_error() from error
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand Brain profile was not found.",
            )

    def get_active_context(self) -> BrandContextSummary:
        brand = self._read(lambda: self.repository.get_active())
        if brand is None:
            return BrandContextSummary()

        context_parts = [
            f"Brand name: {brand.brand_name}",
            f"Company profile: {brand.company_profile}",
            f"Mission: {brand.mission}",
            f"Vision: {brand.vision}",
            f"Industry: {brand.industry}",
            f"Target audience: {brand.target_audience}",
            f"ICP: {brand.icp}",
            f"Brand voice: {brand.brand_voice}",
            f"Tone guidelines: {brand.tone_guidelines}",
            f"Writing style: {brand.writing_style}",
            self._join("Core values", brand.core_values),
            self._join("Value propositions", brand.value_propositions),
            self._join("Proof points", brand.proof_points),
            self._join("Preferred CTAs", brand.preferred_ctas),
            self._join("Preferred hashtags", brand.preferred_hashtags),
            self._join("Forbidden phrases", brand.forbidden_phrases),
            self._join("Preferred terminology", brand.preferred_terminology),
            self._join("Languages", brand.languages),
            self._join("Regional preferences", brand.regional_preferences),
            self._join(
                "Products and services",
                [
                    f"{item.name}: {item.description} {item.value}".strip()
                    for item in brand.products_and_services
                ],
            ),
            self._join(
                "Buyer personas",
                [
                    f"{item.name} ({item.role}) goals={', '.join(item.goals)}"
                    for item in brand.buyer_personas
                ],
            ),
            self._join("Competitors", [item.name for item in brand.competitors]),
            self._join(
                "Case studies",
                [f"{item.title}: {item.summary} {item.outcome}".strip() for item in brand.case_studies],
            ),
            self._join("Website URLs", [str(url) for url in brand.website_urls]),
            self._join("Social media URLs", [str(url) for url in brand.social_media_urls]),
        ]
        context = "\n".join(part for part in context_parts if part and not part.endswith(": "))

        return BrandContextSummary(
            brand_id=brand.id,
            brand_name=brand.brand_name,
            context=context[: settings.brand_context_max_characters],
            applied=bool(context.strip()),
        )

    def _join(self, label: str, values: list[str]) -> str:
        cleaned = [value.strip() for value in values if value and value.strip()]
        return f"{label}: {', '.join(cleaned)}" if cleaned else ""

    def _read(self, reader):
        try:
            return reader()
        except BrandRepositoryError as error:
            raise self._storage_error() from error

    def _storage_error(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Brand Brain storage is unavailable or corrupted.",
        )


def get_brand_repository() -> BrandRepository:
    return BrandRepository(Path(settings.brand_store_path))


def get_brand_service() -> BrandService:
    return BrandService(get_brand_repository())
