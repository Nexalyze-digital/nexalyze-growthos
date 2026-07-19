from abc import ABC, abstractmethod

from app.schemas.research import ResearchProviderResult, ResearchRunCreate


class ResearchProvider(ABC):
    name: str

    @abstractmethod
    def run(
        self, request: ResearchRunCreate, protected_context: str
    ) -> ResearchProviderResult:
        raise NotImplementedError


class ResearchProviderUnavailableError(RuntimeError):
    pass


class ResearchProviderResponseError(RuntimeError):
    pass
