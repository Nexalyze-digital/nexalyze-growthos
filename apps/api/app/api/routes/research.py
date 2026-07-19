from fastapi import APIRouter, Depends, Response, status

from app.schemas.research import ResearchRun, ResearchRunCreate, ResearchRunList
from app.services.research_service import ResearchService, get_research_service

router = APIRouter(prefix="/research", tags=["research"])


@router.post("/runs", response_model=ResearchRun, status_code=status.HTTP_201_CREATED)
def create_research_run(
    payload: ResearchRunCreate,
    service: ResearchService = Depends(get_research_service),
) -> ResearchRun:
    return service.create_run(payload)


@router.get("/runs", response_model=ResearchRunList)
def list_research_runs(
    service: ResearchService = Depends(get_research_service),
) -> ResearchRunList:
    return service.list_runs()


@router.get("/runs/{run_id}", response_model=ResearchRun)
def get_research_run(
    run_id: str,
    service: ResearchService = Depends(get_research_service),
) -> ResearchRun:
    return service.get_run(run_id)


@router.delete("/runs/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_research_run(
    run_id: str,
    service: ResearchService = Depends(get_research_service),
) -> Response:
    service.delete_run(run_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/runs/{run_id}/regenerate", response_model=ResearchRun)
def regenerate_research_run(
    run_id: str,
    service: ResearchService = Depends(get_research_service),
) -> ResearchRun:
    return service.regenerate_run(run_id)
