from fastapi import APIRouter

from app.core.config import settings
from app.providers.ollama import is_ollama_reachable

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "healthy",
        "service": "growthos-api",
        "version": settings.version,
        "ai_provider": settings.ai_provider,
        "ollama_reachable": is_ollama_reachable(settings.ollama_base_url)
        if settings.ai_provider.lower() == "ollama"
        else False,
    }
