from pathlib import Path

from fastapi import HTTPException, status

from app.core.config import settings
from app.providers.research_base import (
    ResearchProvider,
    ResearchProviderResponseError,
    ResearchProviderUnavailableError,
)
from app.providers.research_mock import ResearchMockProvider
from app.providers.research_ollama import ResearchOllamaProvider
from app.repositories.research_repository import ResearchRepository, ResearchRepositoryError
from app.schemas.research import ResearchRun, ResearchRunCreate, ResearchRunList, SourceNote, utc_now
from app.services.brand_service import get_brand_service


class ResearchService:
    def __init__(self, repository: ResearchRepository, provider: ResearchProvider) -> None:
        self.repository = repository
        self.provider = provider

    def list_runs(self) -> ResearchRunList:
        return ResearchRunList(runs=self._read(lambda: self.repository.list()))

    def get_run(self, run_id: str) -> ResearchRun:
        run = self._read(lambda: self.repository.get(run_id))
        if run is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research run was not found.")
        return run

    def create_run(self, request: ResearchRunCreate) -> ResearchRun:
        run = self._execute(request)
        try:
            return self.repository.create(run)
        except ResearchRepositoryError as error:
            raise self._storage_error() from error

    def regenerate_run(self, run_id: str) -> ResearchRun:
        existing = self.get_run(run_id)
        request = ResearchRunCreate(**existing.model_dump())
        regenerated = self._execute(request).model_copy(
            update={"id": existing.id, "created_at": existing.created_at, "updated_at": utc_now()}
        )
        try:
            return self.repository.update(regenerated)
        except ResearchRepositoryError as error:
            raise self._storage_error() from error

    def delete_run(self, run_id: str) -> None:
        try:
            deleted = self.repository.delete(run_id)
        except ResearchRepositoryError as error:
            raise self._storage_error() from error
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research run was not found.")

    def _execute(self, request: ResearchRunCreate) -> ResearchRun:
        protected_context, brand_context_used = self._brand_context(request.brand_id)
        try:
            result = self.provider.run(request, protected_context)
            provider_name = self.provider.name
        except (ResearchProviderUnavailableError, ResearchProviderResponseError):
            if settings.ai_fallback_provider.lower() != "mock":
                raise
            result = ResearchMockProvider().run(request, protected_context)
            provider_name = "mock-fallback"

        return ResearchRun(
            **request.model_dump(),
            **result.model_dump(),
            source_notes=self._source_notes(request),
            provider=provider_name,
            brand_context_used=brand_context_used,
        )

    def _brand_context(self, brand_id: str | None) -> tuple[str, bool]:
        if not brand_id:
            return "", False
        brand_service = get_brand_service()
        brand = brand_service.get_brand(brand_id)
        context = brand_service.get_context_for_brand(brand)
        if not context.applied:
            return "", False
        protected = (
            "Protected Brand Brain research context, highest priority. "
            "Apply company, industry, audience, offer, competitor, terminology, and regional context. "
            "If user instructions conflict with Brand Brain, follow Brand Brain.\n\n"
            f"{context.context[: settings.research_context_max_characters]}"
        )
        return protected, True

    def _source_notes(self, request: ResearchRunCreate) -> list[SourceNote]:
        if request.source_urls:
            return [
                SourceNote(
                    label=f"Supplied source {index + 1}",
                    url=url,
                    note="User-supplied source URL. GrowthOS did not fetch or verify this source in v0.4.0.",
                )
                for index, url in enumerate(request.source_urls)
            ]
        return [
            SourceNote(
                label="AI-generated synthesis",
                url=None,
                note="AI-generated synthesis. No live web research performed.",
            )
        ]

    def _read(self, reader):
        try:
            return reader()
        except ResearchRepositoryError as error:
            raise self._storage_error() from error

    def _storage_error(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Research storage is unavailable or corrupted.",
        )


def get_research_repository() -> ResearchRepository:
    return ResearchRepository(Path(settings.research_store_path))


def get_research_provider() -> ResearchProvider:
    if settings.ai_provider.lower() == "ollama":
        return ResearchOllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout_seconds=settings.ollama_timeout_seconds,
        )
    return ResearchMockProvider()


def get_research_service() -> ResearchService:
    return ResearchService(get_research_repository(), get_research_provider())
