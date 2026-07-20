from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import RequestContext, get_request_context
from app.schemas.publishing import (
    ApprovalResponse,
    DraftCreate,
    DraftDuplicateRequest,
    DraftListResponse,
    DraftResponse,
    DraftUpdate,
    DraftVersionListResponse,
    PublishingJobListResponse,
    PublishingJobResponse,
    PublishingAuditHistoryResponse,
    PublishingProcessRequest,
    ReviewCommentCreate,
    ReviewHistoryResponse,
    ScheduleCreate,
    ScheduleResponse,
    ScheduleUpdate,
    WorkspacePublishingSettingsResponse,
    WorkspacePublishingSettingsUpdate,
)
from app.services.approval_service import ApprovalService
from app.services.draft_service import DraftService
from app.services.publishing_queue_service import PublishingQueueService
from app.services.schedule_service import ScheduleService

router = APIRouter(prefix="/publishing", tags=["publishing"])


@router.post("/drafts", response_model=DraftResponse, status_code=status.HTTP_201_CREATED)
def create_draft(payload: DraftCreate, context: RequestContext = Depends(get_request_context)) -> DraftResponse:
    return _draft_service(context).create(payload)


@router.get("/drafts", response_model=DraftListResponse)
def list_drafts(
    search: str | None = Query(default=None, max_length=200),
    platform: str | None = Query(default=None, max_length=40),
    status_value: str | None = Query(default=None, alias="status", max_length=32),
    archived: bool = False,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    context: RequestContext = Depends(get_request_context),
) -> DraftListResponse:
    return _draft_service(context).list(search, platform, status_value, archived, page, page_size)


@router.get("/drafts/{draft_id}", response_model=DraftResponse)
def get_draft(draft_id: str, context: RequestContext = Depends(get_request_context)) -> DraftResponse:
    return _draft_service(context).get(draft_id)


@router.put("/drafts/{draft_id}", response_model=DraftResponse)
def update_draft(draft_id: str, payload: DraftUpdate, context: RequestContext = Depends(get_request_context)) -> DraftResponse:
    return _draft_service(context).update(draft_id, payload)


@router.post("/drafts/{draft_id}/duplicate", response_model=DraftResponse, status_code=status.HTTP_201_CREATED)
def duplicate_draft(
    draft_id: str,
    payload: DraftDuplicateRequest | None = None,
    context: RequestContext = Depends(get_request_context),
) -> DraftResponse:
    return _draft_service(context).duplicate(draft_id, payload or DraftDuplicateRequest())


@router.post("/drafts/{draft_id}/archive", response_model=DraftResponse)
def archive_draft(draft_id: str, context: RequestContext = Depends(get_request_context)) -> DraftResponse:
    return _draft_service(context).archive(draft_id)


@router.post("/drafts/{draft_id}/restore", response_model=DraftResponse)
def restore_draft(draft_id: str, context: RequestContext = Depends(get_request_context)) -> DraftResponse:
    return _draft_service(context).restore(draft_id)


@router.get("/drafts/{draft_id}/versions", response_model=DraftVersionListResponse)
def list_draft_versions(draft_id: str, context: RequestContext = Depends(get_request_context)) -> DraftVersionListResponse:
    return _draft_service(context).versions(draft_id)


@router.post("/drafts/{draft_id}/submit", response_model=ApprovalResponse)
def submit_draft(draft_id: str, context: RequestContext = Depends(get_request_context)) -> ApprovalResponse:
    return _approval_service(context).submit(draft_id)


@router.post("/drafts/{draft_id}/approve", response_model=ApprovalResponse)
def approve_draft(
    draft_id: str,
    payload: ReviewCommentCreate | None = None,
    context: RequestContext = Depends(get_request_context),
) -> ApprovalResponse:
    return _approval_service(context).approve(draft_id, payload)


@router.post("/drafts/{draft_id}/reject", response_model=ApprovalResponse)
def reject_draft(draft_id: str, payload: ReviewCommentCreate, context: RequestContext = Depends(get_request_context)) -> ApprovalResponse:
    return _approval_service(context).reject(draft_id, payload)


@router.post("/drafts/{draft_id}/request-revision", response_model=ApprovalResponse)
def request_revision(
    draft_id: str,
    payload: ReviewCommentCreate,
    context: RequestContext = Depends(get_request_context),
) -> ApprovalResponse:
    return _approval_service(context).request_revision(draft_id, payload)


@router.post("/approvals/{approval_id}/comments", response_model=ApprovalResponse)
def add_approval_comment(
    approval_id: str,
    payload: ReviewCommentCreate,
    context: RequestContext = Depends(get_request_context),
) -> ApprovalResponse:
    return _approval_service(context).add_comment(approval_id, payload)


@router.get("/drafts/{draft_id}/review-history", response_model=ReviewHistoryResponse)
def review_history(draft_id: str, context: RequestContext = Depends(get_request_context)) -> ReviewHistoryResponse:
    return _approval_service(context).history(draft_id)


@router.post("/drafts/{draft_id}/schedule", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
def schedule_draft(draft_id: str, payload: ScheduleCreate, context: RequestContext = Depends(get_request_context)) -> ScheduleResponse:
    return _schedule_service(context).schedule(draft_id, payload)


@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
def reschedule(schedule_id: str, payload: ScheduleUpdate, context: RequestContext = Depends(get_request_context)) -> ScheduleResponse:
    return _schedule_service(context).reschedule(schedule_id, payload)


@router.post("/schedules/{schedule_id}/unschedule", response_model=ScheduleResponse)
def unschedule(schedule_id: str, context: RequestContext = Depends(get_request_context)) -> ScheduleResponse:
    return _schedule_service(context).unschedule(schedule_id)


@router.post("/drafts/{draft_id}/enqueue", response_model=PublishingJobResponse, status_code=status.HTTP_201_CREATED)
def enqueue_draft(draft_id: str, context: RequestContext = Depends(get_request_context)) -> PublishingJobResponse:
    return _queue_service(context).enqueue(draft_id)


@router.get("/jobs", response_model=PublishingJobListResponse)
def list_jobs(context: RequestContext = Depends(get_request_context)) -> PublishingJobListResponse:
    return _queue_service(context).list()


@router.post("/jobs/process-next", response_model=PublishingJobListResponse)
def process_next_jobs(
    payload: PublishingProcessRequest | None = None,
    context: RequestContext = Depends(get_request_context),
) -> PublishingJobListResponse:
    return _queue_service(context).process_next((payload or PublishingProcessRequest()).limit)


@router.get("/jobs/{job_id}", response_model=PublishingJobResponse)
def get_job(job_id: str, context: RequestContext = Depends(get_request_context)) -> PublishingJobResponse:
    return _queue_service(context).get(job_id)


@router.post("/jobs/{job_id}/process", response_model=PublishingJobResponse)
def process_job(job_id: str, context: RequestContext = Depends(get_request_context)) -> PublishingJobResponse:
    return _queue_service(context).process(job_id)


@router.post("/jobs/{job_id}/retry", response_model=PublishingJobResponse)
def retry_job(job_id: str, context: RequestContext = Depends(get_request_context)) -> PublishingJobResponse:
    return _queue_service(context).retry(job_id)


@router.post("/jobs/{job_id}/cancel", response_model=PublishingJobResponse)
def cancel_job(job_id: str, context: RequestContext = Depends(get_request_context)) -> PublishingJobResponse:
    return _queue_service(context).cancel(job_id)


@router.get("/jobs/{job_id}/audit-history", response_model=PublishingAuditHistoryResponse)
def job_audit_history(job_id: str, context: RequestContext = Depends(get_request_context)) -> PublishingAuditHistoryResponse:
    return _queue_service(context).audit_history(job_id)


@router.get("/settings", response_model=WorkspacePublishingSettingsResponse)
def get_publishing_settings(context: RequestContext = Depends(get_request_context)) -> WorkspacePublishingSettingsResponse:
    return _queue_service(context).get_settings()


@router.put("/settings", response_model=WorkspacePublishingSettingsResponse)
def update_publishing_settings(
    payload: WorkspacePublishingSettingsUpdate,
    context: RequestContext = Depends(get_request_context),
) -> WorkspacePublishingSettingsResponse:
    return _queue_service(context).update_settings(payload)


def _draft_service(context: RequestContext) -> DraftService:
    return DraftService(context.db, context.workspace_id, context.user.id, context.role)


def _approval_service(context: RequestContext) -> ApprovalService:
    return ApprovalService(context.db, context.workspace_id, context.user.id, context.role)


def _schedule_service(context: RequestContext) -> ScheduleService:
    return ScheduleService(context.db, context.workspace_id, context.user.id, context.role)


def _queue_service(context: RequestContext) -> PublishingQueueService:
    return PublishingQueueService(context.db, context.workspace_id, context.user.id, context.role)
