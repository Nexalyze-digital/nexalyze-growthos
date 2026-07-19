from fastapi import APIRouter, Depends

from app.api.dependencies import RequestContext, require_editor
from app.repositories.brand_db_repository import BrandDbRepository
from app.schemas.content import ContentGenerationRequest, ContentGenerationResponse
from app.services.brand_service import BrandService
from app.services.content_service import ContentService, get_configured_provider

router = APIRouter(prefix="/content", tags=["content"])


@router.post("/generate", response_model=ContentGenerationResponse)
def generate_content(
    request: ContentGenerationRequest,
    context: RequestContext = Depends(require_editor),
) -> ContentGenerationResponse:
    service = ContentService(
        provider=get_configured_provider(),
        brand_service=BrandService(
            BrandDbRepository(context.db, context.workspace_id),
            user_id=context.user.id,
            workspace_id=context.workspace_id,
        ),
    )
    return service.generate(request)
