from app.providers.base import ContentProvider
from app.providers.mock import MockContentProvider
from app.schemas.content import ContentGenerationRequest, ContentGenerationResponse


class ContentService:
    def __init__(self, provider: ContentProvider) -> None:
        self.provider = provider

    def generate(
        self, request: ContentGenerationRequest
    ) -> ContentGenerationResponse:
        return self.provider.generate(request)


def get_content_service() -> ContentService:
    return ContentService(provider=MockContentProvider())
