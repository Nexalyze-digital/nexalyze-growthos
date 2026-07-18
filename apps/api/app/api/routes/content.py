from fastapi import APIRouter, Depends

from app.schemas.content import ContentGenerationRequest, ContentGenerationResponse
from app.services.content_service import ContentService, get_content_service

router = APIRouter(prefix="/content", tags=["content"])


@router.post("/generate", response_model=ContentGenerationResponse)
def generate_content(
    request: ContentGenerationRequest,
    service: ContentService = Depends(get_content_service),
) -> ContentGenerationResponse:
    return service.generate(request)
