from fastapi import APIRouter, Depends, Response, status

from app.api.dependencies import RequestContext, get_request_context, require_editor
from app.repositories.brand_db_repository import BrandDbRepository
from app.repositories.research_db_repository import ResearchDbRepository
from app.schemas.research import ResearchRun, ResearchRunCreate, ResearchRunList
from app.services.brand_service import BrandService
from app.services.research_service import ResearchService, get_research_provider

router = APIRouter(prefix="/research", tags=["research"])


@router.post("/runs", response_model=ResearchRun, status_code=status.HTTP_201_CREATED)
def create_research_run(
    payload: ResearchRunCreate,
    context: RequestContext = Depends(require_editor),
) -> ResearchRun:
    return _service(context).create_run(payload)


@router.get("/runs", response_model=ResearchRunList)
def list_research_runs(
    context: RequestContext = Depends(get_request_context),
) -> ResearchRunList:
    return _service(context).list_runs()


@router.get("/runs/{run_id}", response_model=ResearchRun)
def get_research_run(
    run_id: str,
    context: RequestContext = Depends(get_request_context),
) -> ResearchRun:
    return _service(context).get_run(run_id)


@router.delete("/runs/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_research_run(
    run_id: str,
    context: RequestContext = Depends(require_editor),
) -> Response:
    _service(context).delete_run(run_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/runs/{run_id}/regenerate", response_model=ResearchRun)
def regenerate_research_run(
    run_id: str,
    context: RequestContext = Depends(require_editor),
) -> ResearchRun:
    return _service(context).regenerate_run(run_id)


def _service(context: RequestContext) -> ResearchService:
    brand_service = BrandService(
        BrandDbRepository(context.db, context.workspace_id),
        user_id=context.user.id,
        workspace_id=context.workspace_id,
    )
    return ResearchService(
        ResearchDbRepository(context.db, context.workspace_id),
        get_research_provider(),
        user_id=context.user.id,
        workspace_id=context.workspace_id,
        brand_service=brand_service,
    )
