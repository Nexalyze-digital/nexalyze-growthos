from app.core.config import settings
from app.providers.base import (
    ContentProvider,
    ProviderResponseError,
    ProviderUnavailableError,
)
from app.providers.mock import MockContentProvider
from app.providers.ollama import OllamaContentProvider
from app.schemas.content import ContentGenerationRequest, ContentGenerationResponse


class ContentService:
    def __init__(self, provider: ContentProvider) -> None:
        self.provider = provider

    def generate(
        self, request: ContentGenerationRequest
    ) -> ContentGenerationResponse:
        try:
            return self.provider.generate(request)
        except (ProviderUnavailableError, ProviderResponseError):
            if settings.ai_fallback_provider.lower() != "mock":
                raise
            fallback_response = MockContentProvider().generate(request)
            return fallback_response.model_copy(update={"provider": "mock-fallback"})


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
