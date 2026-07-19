from fastapi import APIRouter, Depends, Response, status

from app.schemas.brand import BrandBrain, BrandBrainCreate, BrandBrainList, BrandBrainUpdate
from app.services.brand_service import BrandService, get_brand_service

router = APIRouter(prefix="/brands", tags=["brands"])


@router.get("", response_model=BrandBrainList)
def list_brands(service: BrandService = Depends(get_brand_service)) -> BrandBrainList:
    return BrandBrainList(brands=service.list_brands())


@router.post("", response_model=BrandBrain, status_code=status.HTTP_201_CREATED)
def create_brand(
    payload: BrandBrainCreate,
    service: BrandService = Depends(get_brand_service),
) -> BrandBrain:
    return service.create_brand(payload)


@router.get("/{brand_id}", response_model=BrandBrain)
def get_brand(
    brand_id: str,
    service: BrandService = Depends(get_brand_service),
) -> BrandBrain:
    return service.get_brand(brand_id)


@router.put("/{brand_id}", response_model=BrandBrain)
def update_brand(
    brand_id: str,
    payload: BrandBrainUpdate,
    service: BrandService = Depends(get_brand_service),
) -> BrandBrain:
    return service.update_brand(brand_id, payload)


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand(
    brand_id: str,
    service: BrandService = Depends(get_brand_service),
) -> Response:
    service.delete_brand(brand_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
