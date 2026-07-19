import os
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite:///data/test-growthos.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import RequestContext, get_request_context, require_editor
from app.core.config import settings
from app.db.models import Base, Organization, User, Workspace, WorkspaceMembership
from app.db.session import SessionLocal, engine
from app.core.security import hash_password
from app.schemas.auth import WorkspaceRole
from main import app


@pytest.fixture(autouse=True)
def clean_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "brand_store_path", str(tmp_path / "brands.json"))
    monkeypatch.setattr(settings, "research_store_path", str(tmp_path / "research.json"))
    monkeypatch.setattr(settings, "ai_provider", "mock")
    monkeypatch.setattr(settings, "ai_fallback_provider", "mock")
    monkeypatch.setattr(settings, "auth_rate_limit_per_minute", 1000)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        user = User(
            id="test-user",
            email="test@example.com",
            name="Test User",
            password_hash=hash_password("StrongPass123"),
            is_active=True,
        )
        organization = Organization(id="test-org", name="Test Organization", owner_user_id=user.id)
        workspace = Workspace(id="test-workspace", organization_id=organization.id, name="Test Workspace")
        membership = WorkspaceMembership(
            id="test-membership",
            workspace_id=workspace.id,
            user_id=user.id,
            role=WorkspaceRole.owner.value,
        )
        db.add(user)
        db.flush()
        db.add(organization)
        db.flush()
        db.add(workspace)
        db.flush()
        db.add(membership)
        db.commit()

    def override_context():
        with SessionLocal() as db:
            user = db.get(User, "test-user")
            yield RequestContext(
                user=user,
                workspace_id="test-workspace",
                role=WorkspaceRole.owner,
                db=db,
            )

    app.dependency_overrides[get_request_context] = override_context
    app.dependency_overrides[require_editor] = override_context
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client):
    app.dependency_overrides.clear()
    payload = {
        "email": "owner@example.com",
        "password": "StrongPass123",
        "name": "Owner User",
        "organization_name": "Nexalyze",
        "workspace_name": "Default Workspace",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
