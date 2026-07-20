from datetime import datetime, timedelta, timezone

from app.db.models import WorkspaceMembership
from app.db.session import SessionLocal
from app.schemas.auth import WorkspaceRole
from tests.test_platform_api import auth_headers, register
from tests.test_publishing_api import allow_self_approval, valid_draft_payload


def _approved_job(client, headers, workspace_id: str, **draft_overrides):
    draft = client.post("/api/v1/publishing/drafts", headers=headers, json=valid_draft_payload(**draft_overrides))
    assert draft.status_code == 201
    draft_id = draft.json()["id"]
    submitted = client.post(f"/api/v1/publishing/drafts/{draft_id}/submit", headers=headers)
    assert submitted.status_code == 200
    allow_self_approval(workspace_id)
    approved = client.post(f"/api/v1/publishing/drafts/{draft_id}/approve", headers=headers, json={"body": "Approved."})
    assert approved.status_code == 200
    job = client.post(f"/api/v1/publishing/drafts/{draft_id}/enqueue", headers=headers)
    assert job.status_code == 201
    return draft_id, job.json()["id"]


def test_mock_processing_success_publishes_and_records_audit(client):
    token_payload = register(client, "publisher-success@example.com")
    headers = auth_headers(token_payload)
    draft_id, job_id = _approved_job(client, headers, token_payload["active_workspace_id"])

    processed = client.post(f"/api/v1/publishing/jobs/{job_id}/process", headers=headers)
    assert processed.status_code == 200
    payload = processed.json()
    assert payload["status"] == "published"
    assert payload["attempts"][0]["provider_post_id"].startswith("mock-linkedin-")
    assert payload["attempts"][0]["published_at"]

    draft = client.get(f"/api/v1/publishing/drafts/{draft_id}", headers=headers)
    assert draft.status_code == 200
    assert draft.json()["status"] == "published"

    history = client.get(f"/api/v1/publishing/jobs/{job_id}/audit-history", headers=headers)
    assert history.status_code == 200
    actions = [event["action"] for event in history.json()["events"]]
    assert actions == ["created", "queued", "processing", "published"]


def test_transient_failure_uses_exponential_retry_then_manual_retry(client):
    token_payload = register(client, "publisher-transient@example.com")
    headers = auth_headers(token_payload)
    settings = client.put(
        "/api/v1/publishing/settings",
        headers=headers,
        json={"mock_provider_behavior": "transient_failure", "retry_backoff_base_seconds": 2, "max_retry_count": 2},
    )
    assert settings.status_code == 200
    _, job_id = _approved_job(client, headers, token_payload["active_workspace_id"])

    first = client.post(f"/api/v1/publishing/jobs/{job_id}/process", headers=headers)
    assert first.status_code == 200
    first_payload = first.json()
    assert first_payload["status"] == "retry_pending"
    assert first_payload["retry_count"] == 1
    assert first_payload["next_retry_at"]
    assert first_payload["attempts"][0]["error_category"] == "transient"

    retry = client.post(f"/api/v1/publishing/jobs/{job_id}/retry", headers=headers)
    assert retry.status_code == 200
    assert retry.json()["status"] == "retry_pending"
    assert retry.json()["retry_count"] == 2

    second = client.post(f"/api/v1/publishing/jobs/{job_id}/process", headers=headers)
    assert second.status_code == 200
    assert second.json()["status"] == "dead_letter"


def test_permanent_failure_moves_directly_to_dead_letter(client):
    token_payload = register(client, "publisher-permanent@example.com")
    headers = auth_headers(token_payload)
    _, job_id = _approved_job(
        client,
        headers,
        token_payload["active_workspace_id"],
        body="A draft that should not publish. [mock:permanent]",
    )

    processed = client.post("/api/v1/publishing/jobs/process-next", headers=headers, json={"limit": 1})
    assert processed.status_code == 200
    jobs = processed.json()["jobs"]
    assert len(jobs) == 1
    assert jobs[0]["id"] == job_id
    assert jobs[0]["status"] == "dead_letter"
    assert jobs[0]["error_category"] == "permanent"


def test_processing_settings_are_owner_scoped_and_validated(client):
    token_payload = register(client, "publisher-settings@example.com")
    headers = auth_headers(token_payload)

    default_settings = client.get("/api/v1/publishing/settings", headers=headers)
    assert default_settings.status_code == 200
    assert default_settings.json()["queue_concurrency"] == 1

    updated = client.put(
        "/api/v1/publishing/settings",
        headers=headers,
        json={"queue_concurrency": 2, "max_retry_count": 4, "mock_provider_behavior": "success"},
    )
    assert updated.status_code == 200
    assert updated.json()["queue_concurrency"] == 2
    assert updated.json()["max_retry_count"] == 4

    invalid = client.put("/api/v1/publishing/settings", headers=headers, json={"queue_concurrency": 0})
    assert invalid.status_code == 422

    with SessionLocal() as db:
        membership = db.query(WorkspaceMembership).filter_by(workspace_id=token_payload["active_workspace_id"]).one()
        membership.role = WorkspaceRole.editor.value
        db.commit()
    denied = client.put("/api/v1/publishing/settings", headers=headers, json={"queue_concurrency": 3})
    assert denied.status_code == 403


def test_viewer_cannot_process_retry_or_cancel(client):
    token_payload = register(client, "publisher-viewer-processing@example.com")
    headers = auth_headers(token_payload)
    _, job_id = _approved_job(client, headers, token_payload["active_workspace_id"])

    with SessionLocal() as db:
        membership = db.query(WorkspaceMembership).filter_by(workspace_id=token_payload["active_workspace_id"]).one()
        membership.role = WorkspaceRole.viewer.value
        db.commit()

    assert client.post(f"/api/v1/publishing/jobs/{job_id}/process", headers=headers).status_code == 403
    assert client.post(f"/api/v1/publishing/jobs/{job_id}/retry", headers=headers).status_code == 403
    assert client.post(f"/api/v1/publishing/jobs/{job_id}/cancel", headers=headers).status_code == 403


def test_workspace_isolation_blocks_queue_processing_visibility(client):
    first = register(client, "publisher-workspace-a@example.com")
    first_headers = auth_headers(first)
    _, job_id = _approved_job(client, first_headers, first["active_workspace_id"])

    second = register(client, "publisher-workspace-b@example.com")
    second_headers = auth_headers(second)

    hidden = client.get(f"/api/v1/publishing/jobs/{job_id}", headers=second_headers)
    assert hidden.status_code == 404
    hidden_history = client.get(f"/api/v1/publishing/jobs/{job_id}/audit-history", headers=second_headers)
    assert hidden_history.status_code == 404


def test_processing_waits_for_retry_window(client):
    token_payload = register(client, "publisher-retry-window@example.com")
    headers = auth_headers(token_payload)
    _, job_id = _approved_job(client, headers, token_payload["active_workspace_id"], body="[mock:transient] Retry later.")
    first = client.post(f"/api/v1/publishing/jobs/{job_id}/process", headers=headers)
    assert first.status_code == 200
    with SessionLocal() as db:
        from app.db.models import PublishingJob

        job = db.get(PublishingJob, job_id)
        job.next_retry_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        db.commit()

    blocked = client.post(f"/api/v1/publishing/jobs/{job_id}/process", headers=headers)
    assert blocked.status_code == 409
