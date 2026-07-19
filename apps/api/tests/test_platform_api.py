import json
from pathlib import Path

from app.core.config import settings
from app.core.config import Settings
from app.core.security import create_access_token
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


def test_missing_and_expired_access_token_are_rejected(client, monkeypatch):
    app.dependency_overrides.clear()
    missing = client.get("/api/v1/auth/me")
    assert missing.status_code == 401

    token_payload = register(client)
    monkeypatch.setattr(settings, "access_token_expire_minutes", -1)
    expired_token, _ = create_access_token(token_payload["user"]["id"], token_payload["active_workspace_id"])

    expired = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert expired.status_code == 401


def test_production_environment_requires_strong_jwt_secret():
    try:
        Settings(app_env="production", jwt_secret_key="local-development-secret-change-me")
    except ValueError as error:
        assert "JWT_SECRET_KEY" in str(error)
    else:
        raise AssertionError("Expected production settings with the default JWT secret to fail.")


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


def test_duplicate_registration_and_invalid_refresh_token(client):
    register(client)

    duplicate = client.post(
        "/api/v1/auth/register",
        json={
            "email": "owner@example.com",
            "password": "StrongPass123",
            "name": "Owner User",
            "organization_name": "Nexalyze",
            "workspace_name": "Default Workspace",
        },
    )
    assert duplicate.status_code == 409

    invalid_refresh = client.post("/api/v1/auth/refresh", json={"refresh_token": "not-a-real-refresh-token"})
    assert invalid_refresh.status_code == 401


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


def test_logout_revokes_refresh_token(client):
    token_payload = register(client)

    logout = client.post(
        "/api/v1/auth/logout",
        headers=auth_headers(token_payload),
        json={"refresh_token": token_payload["refresh_token"]},
    )
    assert logout.status_code == 204

    reused = client.post("/api/v1/auth/refresh", json={"refresh_token": token_payload["refresh_token"]})
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


def test_cross_workspace_read_and_update_attempts_are_rejected(client):
    owner_payload = register(client, "owner-one@example.com")
    owner_headers = auth_headers(owner_payload)
    brand = client.post("/api/v1/brands", headers=owner_headers, json=valid_brand_payload()).json()

    second_payload = register(client, "owner-two@example.com")
    second_headers = auth_headers(second_payload)

    cross_workspace_read = client.get(
        f"/api/v1/brands/{brand['id']}",
        headers={**second_headers, "X-Workspace-Id": owner_payload["active_workspace_id"]},
    )
    assert cross_workspace_read.status_code == 403

    cross_workspace_update = client.put(
        f"/api/v1/brands/{brand['id']}",
        headers={**owner_headers, "X-Workspace-Id": second_payload["active_workspace_id"]},
        json={"mission": "This should not cross workspaces."},
    )
    assert cross_workspace_update.status_code == 403


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

    update = client.put("/api/v1/brands/not-owned", headers=headers, json={"mission": "Denied"})
    assert update.status_code == 403

    delete = client.delete("/api/v1/brands/not-owned", headers=headers)
    assert delete.status_code == 403


def test_editor_cannot_create_workspace(client):
    token_payload = register(client)
    workspace_id = token_payload["active_workspace_id"]
    headers = auth_headers(token_payload)

    with SessionLocal() as db:
        membership = db.query(WorkspaceMembership).filter_by(workspace_id=workspace_id).one()
        membership.role = WorkspaceRole.editor.value
        db.commit()

    response = client.post("/api/v1/auth/workspaces", headers=headers, json={"name": "Admin Only"})

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

    brand["id"] = "legacy-brand-1"
    research["id"] = "legacy-research-1"
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


def test_json_migration_is_idempotent_and_skips_duplicate_records(client, tmp_path: Path):
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
    brand["id"] = "legacy-brand-duplicate"
    research["id"] = "legacy-research-duplicate"
    brand_path.write_text(json.dumps({"brands": [brand, brand]}), encoding="utf-8")
    research_path.write_text(json.dumps({"runs": [research, research]}), encoding="utf-8")

    from app.services.migration_service import JsonMigrationService

    with SessionLocal() as db:
        first = JsonMigrationService(db, workspace_id).migrate(dry_run=False)
        second = JsonMigrationService(db, workspace_id).migrate(dry_run=False)

    assert first.brands_found == 2
    assert first.research_runs_found == 2
    assert first.brands_migrated == 1
    assert first.research_runs_migrated == 1
    assert second.brands_migrated == 0
    assert second.research_runs_migrated == 0


def test_json_migration_failure_does_not_create_backups(client, tmp_path: Path):
    token_payload = register(client)
    workspace_id = token_payload["active_workspace_id"]
    brand_path = tmp_path / "brands.json"
    research_path = tmp_path / "research.json"
    settings.brand_store_path = str(brand_path)
    settings.research_store_path = str(research_path)
    brand_path.write_text("{not valid json", encoding="utf-8")
    research_path.write_text(json.dumps({"runs": []}), encoding="utf-8")

    from app.services.migration_service import JsonMigrationService

    with SessionLocal() as db:
        try:
            JsonMigrationService(db, workspace_id).migrate(dry_run=False)
        except json.JSONDecodeError:
            pass
        else:
            raise AssertionError("Expected corrupted JSON migration to fail.")

    assert not brand_path.with_suffix(".json.bak").exists()
    assert not research_path.with_suffix(".json.bak").exists()
