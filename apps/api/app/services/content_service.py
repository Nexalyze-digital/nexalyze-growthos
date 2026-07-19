from app.core.config import settings
from app.providers.base import (
    ContentProvider,
    ProviderResponseError,
    ProviderUnavailableError,
)
from app.providers.mock import MockContentProvider
from app.providers.ollama import OllamaContentProvider
from app.schemas.content import ContentGenerationRequest, ContentGenerationResponse
from app.services.brand_service import get_brand_service


class ContentService:
    def __init__(self, provider: ContentProvider) -> None:
        self.provider = provider

    def generate(
        self, request: ContentGenerationRequest
    ) -> ContentGenerationResponse:
        enriched_request, brand_name, brand_context_applied = self._with_brand_context(
            request
        )
        try:
            response = self.provider.generate(enriched_request)
        except (ProviderUnavailableError, ProviderResponseError):
            if settings.ai_fallback_provider.lower() != "mock":
                raise
            response = MockContentProvider().generate(enriched_request).model_copy(
                update={"provider": "mock-fallback"}
            )

        return response.model_copy(
            update={
                "brand_context_applied": brand_context_applied,
                "brand_name": brand_name,
            }
        )

    def _with_brand_context(
        self, request: ContentGenerationRequest
    ) -> tuple[ContentGenerationRequest, str | None, bool]:
        brand_context = get_brand_service().get_active_context()
        if not brand_context.applied:
            return request, None, False

        existing_instructions = request.instructions.strip() if request.instructions else ""
        enriched_instructions = (
            "Protected Brand Brain instructions, highest priority: "
            "apply this saved brand context to the response. "
            "Do not use forbidden phrases. Prefer the listed terminology, CTAs, hashtags, languages, and regional preferences. "
            "If user instructions conflict with Brand Brain instructions, follow Brand Brain.\n\n"
            f"{brand_context.context}"
        )
        if existing_instructions:
            enriched_instructions = (
                f"{enriched_instructions}\n\nUser request instructions, lower priority: {existing_instructions}"
            )

        return (
            request.model_copy(update={"instructions": enriched_instructions}),
            brand_context.brand_name,
            True,
        )


def get_content_service() -> ContentService:
    return ContentService(provider=get_configured_provider())


def get_configured_provider() -> ContentProvider:
    if settings.ai_provider.lower() == "ollama":
        return OllamaContentProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout_seconds=settings.ollama_timeout_seconds,
        )
    return MockContentProvider()
