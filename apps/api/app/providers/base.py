from abc import ABC, abstractmethod

from app.schemas.content import ContentGenerationRequest, ContentGenerationResponse


class ContentProvider(ABC):
    name: str

    @abstractmethod
    def generate(
        self, request: ContentGenerationRequest
    ) -> ContentGenerationResponse:
        raise NotImplementedError
