from fastapi import APIRouter, Depends, Response, status

from app.api.dependencies import RequestContext, get_request_context, require_editor
from app.repositories.brand_db_repository import BrandDbRepository
from app.schemas.brand import BrandBrain, BrandBrainCreate, BrandBrainList, BrandBrainUpdate
from app.services.brand_service import BrandService

router = APIRouter(prefix="/brands", tags=["brands"])


@router.get("", response_model=BrandBrainList)
def list_brands(context: RequestContext = Depends(get_request_context)) -> BrandBrainList:
    service = _service(context)
    return BrandBrainList(brands=service.list_brands())


@router.post("", response_model=BrandBrain, status_code=status.HTTP_201_CREATED)
def create_brand(
    payload: BrandBrainCreate,
    context: RequestContext = Depends(require_editor),
) -> BrandBrain:
    return _service(context).create_brand(payload)


@router.get("/{brand_id}", response_model=BrandBrain)
def get_brand(
    brand_id: str,
    context: RequestContext = Depends(get_request_context),
) -> BrandBrain:
    return _service(context).get_brand(brand_id)


@router.put("/{brand_id}", response_model=BrandBrain)
def update_brand(
    brand_id: str,
    payload: BrandBrainUpdate,
    context: RequestContext = Depends(require_editor),
) -> BrandBrain:
    return _service(context).update_brand(brand_id, payload)


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand(
    brand_id: str,
    context: RequestContext = Depends(require_editor),
) -> Response:
    _service(context).delete_brand(brand_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _service(context: RequestContext) -> BrandService:
    return BrandService(
        BrandDbRepository(context.db, context.workspace_id),
        user_id=context.user.id,
        workspace_id=context.workspace_id,
    )
