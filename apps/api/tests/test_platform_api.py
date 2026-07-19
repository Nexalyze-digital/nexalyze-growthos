import json
from pathlib import Path

from app.core.config import settings
from app.db.models import WorkspaceMembership
from app.db.session import SessionLocal
from main import app
from app.schemas.auth import WorkspaceRole
from tests.test_brand_api import valid_brand_payload
from tests.test_research_api import valid_research_payload


def register(client, email: str = "owner@example.com"):
    app.dependency_overrides.clear()
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "StrongPass123",
            "name": "Owner User",
            "organization_name": "Nexalyze",
            "workspace_name": "Default Workspace",
        },
    )
    assert response.status_code == 201
    return response.json()


def auth_headers(token_payload):
    return {"Authorization": f"Bearer {token_payload['access_token']}"}


def test_registration_login_current_user_and_logout(client):
    token_payload = register(client)

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "StrongPass123"},
    )
    assert login.status_code == 200
    assert login.json()["user"]["email"] == "owner@example.com"

    current = client.get("/api/v1/auth/me", headers=auth_headers(token_payload))
    assert current.status_code == 200
    assert current.json()["active_workspace_id"] == token_payload["active_workspace_id"]

    logout = client.post(
        "/api/v1/auth/logout",
        headers=auth_headers(token_payload),
        json={"refresh_token": token_payload["refresh_token"]},
    )
    assert logout.status_code == 204


def test_password_validation_and_login_errors(client):
    weak = client.post(
        "/api/v1/auth/register",
        json={
            "email": "weak@example.com",
            "password": "weakpass",
            "name": "Weak User",
        },
    )
    assert weak.status_code == 422

    register(client)
    invalid = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "WrongPass123"},
    )
    assert invalid.status_code == 401


def test_refresh_token_rotation(client):
    token_payload = register(client)

    refreshed = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token_payload["refresh_token"]},
    )

    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"] != token_payload["access_token"]

    reused = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token_payload["refresh_token"]},
    )
    assert reused.status_code == 401


def test_workspace_isolation_for_brand_brain(client):
    token_payload = register(client)
    headers = auth_headers(token_payload)

    created = client.post("/api/v1/brands", headers=headers, json=valid_brand_payload())
    assert created.status_code == 201

    workspace = client.post(
        "/api/v1/auth/workspaces",
        headers=headers,
        json={"name": "Second Workspace"},
    )
    assert workspace.status_code == 201
    second_workspace_id = workspace.json()["id"]

    isolated = client.get(
        "/api/v1/brands",
        headers={**headers, "X-Workspace-Id": second_workspace_id},
    )

    assert isolated.status_code == 200
    assert isolated.json()["brands"] == []


def test_viewer_cannot_write_workspace_resources(client):
    token_payload = register(client)
    workspace_id = token_payload["active_workspace_id"]
    headers = auth_headers(token_payload)

    with SessionLocal() as db:
        membership = db.query(WorkspaceMembership).filter_by(workspace_id=workspace_id).one()
        membership.role = WorkspaceRole.viewer.value
        db.commit()

    response = client.post("/api/v1/brands", headers=headers, json=valid_brand_payload())

    assert response.status_code == 403


def test_json_migration_dry_run_and_live(client, tmp_path: Path):
    token_payload = register(client)
    workspace_id = token_payload["active_workspace_id"]
    brand_path = tmp_path / "brands.json"
    research_path = tmp_path / "research.json"
    settings.brand_store_path = str(brand_path)
    settings.research_store_path = str(research_path)

    brand = client.post("/api/v1/brands", headers=auth_headers(token_payload), json=valid_brand_payload()).json()
    research = client.post(
        "/api/v1/research/runs",
        headers=auth_headers(token_payload),
        json=valid_research_payload(),
    ).json()

    brand_path.write_text(json.dumps({"brands": [brand]}), encoding="utf-8")
    research_path.write_text(json.dumps({"runs": [research]}), encoding="utf-8")

    from app.services.migration_service import JsonMigrationService

    with SessionLocal() as db:
        dry_run = JsonMigrationService(db, workspace_id).migrate(dry_run=True)
        live = JsonMigrationService(db, workspace_id).migrate(dry_run=False)

    assert dry_run.brands_found == 1
    assert dry_run.research_runs_found == 1
    assert live.brands_migrated == 1
    assert live.research_runs_migrated == 1
    assert brand_path.with_suffix(".json.bak").exists()
    assert research_path.with_suffix(".json.bak").exists()
