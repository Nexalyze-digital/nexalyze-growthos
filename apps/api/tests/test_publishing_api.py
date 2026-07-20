from datetime import datetime, timedelta, timezone

from app.db.models import PublishingJob, WorkspaceMembership, WorkspacePublishingSettings
from app.db.session import SessionLocal
from app.schemas.auth import WorkspaceRole
from app.schemas.publishing import PublishingJobStatus
from tests.test_platform_api import auth_headers, register


def valid_draft_payload(**overrides):
    payload = {
        "title": "Launch post",
        "body": "A concise publishing draft for GrowthOS.",
        "platform": "LinkedIn",
        "hashtags": ["GrowthOS", "#AI"],
        "brand_id": None,
        "source_research_run_id": None,
    }
    payload.update(overrides)
    return payload


def future_schedule(days: int = 1):
    return {
        "scheduled_at": (datetime.now(timezone.utc) + timedelta(days=days)).isoformat(),
        "timezone": "UTC",
    }


def create_draft(client, headers):
    response = client.post("/api/v1/publishing/drafts", headers=headers, json=valid_draft_payload())
    assert response.status_code == 201
    return response.json()


def allow_self_approval(workspace_id: str):
    with SessionLocal() as db:
        settings = db.query(WorkspacePublishingSettings).filter_by(workspace_id=workspace_id).one_or_none()
        if not settings:
            settings = WorkspacePublishingSettings(workspace_id=workspace_id, prevent_self_approval=False)
            db.add(settings)
        settings.prevent_self_approval = False
        db.commit()


def approve_draft(client, headers, workspace_id: str, draft_id: str):
    submit = client.post(f"/api/v1/publishing/drafts/{draft_id}/submit", headers=headers)
    assert submit.status_code == 200
    allow_self_approval(workspace_id)
    approve = client.post(f"/api/v1/publishing/drafts/{draft_id}/approve", headers=headers, json={"body": "Approved."})
    assert approve.status_code == 200
    return approve.json()


def test_draft_crud_versioning_duplicate_archive_restore(client):
    token_payload = register(client)
    headers = auth_headers(token_payload)
    draft = create_draft(client, headers)

    listed = client.get("/api/v1/publishing/drafts", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    updated = client.put(
        f"/api/v1/publishing/drafts/{draft['id']}",
        headers=headers,
        json=valid_draft_payload(title="Updated launch post", expected_revision=draft["revision"]),
    )
    assert updated.status_code == 200
    assert updated.json()["current_version_number"] == 2

    stale = client.put(
        f"/api/v1/publishing/drafts/{draft['id']}",
        headers=headers,
        json=valid_draft_payload(title="Stale update", expected_revision=draft["revision"]),
    )
    assert stale.status_code == 409

    versions = client.get(f"/api/v1/publishing/drafts/{draft['id']}/versions", headers=headers)
    assert versions.status_code == 200
    assert len(versions.json()["versions"]) == 2

    duplicate = client.post(f"/api/v1/publishing/drafts/{draft['id']}/duplicate", headers=headers, json={})
    assert duplicate.status_code == 201
    assert duplicate.json()["id"] != draft["id"]

    archived = client.post(f"/api/v1/publishing/drafts/{draft['id']}/archive", headers=headers)
    assert archived.status_code == 200
    assert archived.json()["status"] == "archived"

    restored = client.post(f"/api/v1/publishing/drafts/{draft['id']}/restore", headers=headers)
    assert restored.status_code == 200
    assert restored.json()["status"] == "edited"


def test_viewer_cannot_write_but_can_read(client):
    token_payload = register(client)
    headers = auth_headers(token_payload)
    draft = create_draft(client, headers)

    with SessionLocal() as db:
        membership = db.query(WorkspaceMembership).filter_by(workspace_id=token_payload["active_workspace_id"]).one()
        membership.role = WorkspaceRole.viewer.value
        db.commit()

    read = client.get(f"/api/v1/publishing/drafts/{draft['id']}", headers=headers)
    assert read.status_code == 200

    denied = client.post("/api/v1/publishing/drafts", headers=headers, json=valid_draft_payload())
    assert denied.status_code == 403


def test_workspace_isolation_blocks_cross_workspace_draft_access(client):
    first = register(client, "publisher-one@example.com")
    first_headers = auth_headers(first)
    draft = create_draft(client, first_headers)

    second = register(client, "publisher-two@example.com")
    second_headers = auth_headers(second)

    blocked = client.get(
        f"/api/v1/publishing/drafts/{draft['id']}",
        headers={**second_headers, "X-Workspace-Id": first["active_workspace_id"]},
    )
    assert blocked.status_code == 403

    hidden = client.get(f"/api/v1/publishing/drafts/{draft['id']}", headers=second_headers)
    assert hidden.status_code == 404


def test_review_lifecycle_and_self_approval_policy(client):
    token_payload = register(client)
    headers = auth_headers(token_payload)
    draft = create_draft(client, headers)

    submit = client.post(f"/api/v1/publishing/drafts/{draft['id']}/submit", headers=headers)
    assert submit.status_code == 200
    assert submit.json()["status"] == "pending"

    self_approval = client.post(f"/api/v1/publishing/drafts/{draft['id']}/approve", headers=headers, json={"body": "Approved."})
    assert self_approval.status_code == 403

    allow_self_approval(token_payload["active_workspace_id"])
    revision = client.post(
        f"/api/v1/publishing/drafts/{draft['id']}/request-revision",
        headers=headers,
        json={"body": "Please clarify the CTA."},
    )
    assert revision.status_code == 200
    assert revision.json()["status"] == "revision_requested"

    history = client.get(f"/api/v1/publishing/drafts/{draft['id']}/review-history", headers=headers)
    assert history.status_code == 200
    assert history.json()["approvals"][0]["comments"][0]["comment_type"] == "revision_request"


def test_schedule_reschedule_unschedule_and_conflict_validation(client):
    token_payload = register(client)
    headers = auth_headers(token_payload)
    draft = create_draft(client, headers)
    approve_draft(client, headers, token_payload["active_workspace_id"], draft["id"])

    scheduled = client.post(f"/api/v1/publishing/drafts/{draft['id']}/schedule", headers=headers, json=future_schedule())
    assert scheduled.status_code == 201
    assert scheduled.json()["draft_version_id"]

    other = create_draft(client, headers)
    approve_draft(client, headers, token_payload["active_workspace_id"], other["id"])
    conflict = client.post(f"/api/v1/publishing/drafts/{other['id']}/schedule", headers=headers, json=future_schedule())
    assert conflict.status_code == 409

    rescheduled = client.put(
        f"/api/v1/publishing/schedules/{scheduled.json()['id']}",
        headers=headers,
        json=future_schedule(days=2),
    )
    assert rescheduled.status_code == 200

    unscheduled = client.post(f"/api/v1/publishing/schedules/{scheduled.json()['id']}/unschedule", headers=headers)
    assert unscheduled.status_code == 200
    assert unscheduled.json()["status"] == "unscheduled"

    past = client.post(
        f"/api/v1/publishing/drafts/{draft['id']}/schedule",
        headers=headers,
        json={"scheduled_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(), "timezone": "UTC"},
    )
    assert past.status_code == 422


def test_queue_enqueue_idempotency_cancel_and_retry_validation(client):
    token_payload = register(client)
    headers = auth_headers(token_payload)
    draft = create_draft(client, headers)
    approve_draft(client, headers, token_payload["active_workspace_id"], draft["id"])

    job = client.post(f"/api/v1/publishing/drafts/{draft['id']}/enqueue", headers=headers)
    assert job.status_code == 201
    job_id = job.json()["id"]

    duplicate = client.post(f"/api/v1/publishing/drafts/{draft['id']}/enqueue", headers=headers)
    assert duplicate.status_code == 201
    assert duplicate.json()["id"] == job_id

    listed = client.get("/api/v1/publishing/jobs", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()["jobs"]) == 1

    cancelled = client.post(f"/api/v1/publishing/jobs/{job_id}/cancel", headers=headers)
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"

    retry_blocked = client.post(f"/api/v1/publishing/jobs/{job_id}/retry", headers=headers)
    assert retry_blocked.status_code == 409

    with SessionLocal() as db:
        failed = db.get(PublishingJob, job_id)
        failed.status = PublishingJobStatus.failed.value
        failed.error_category = "transient"
        db.commit()

    retried = client.post(f"/api/v1/publishing/jobs/{job_id}/retry", headers=headers)
    assert retried.status_code == 200
    assert retried.json()["retry_count"] == 1
    assert retried.json()["attempts"][0]["status"] == "pending"
