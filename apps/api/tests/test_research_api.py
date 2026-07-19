import json
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_stores(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "brand_store_path", str(tmp_path / "brands.json"))
    monkeypatch.setattr(settings, "research_store_path", str(tmp_path / "research.json"))
    monkeypatch.setattr(settings, "ai_provider", "mock")
    monkeypatch.setattr(settings, "ai_fallback_provider", "mock")
    yield


def valid_research_payload(**overrides):
    payload = {
        "topic": "AI automation for service businesses",
        "objective": "Find practical market opportunities for GrowthOS.",
        "audience": "Founders",
        "industry": "AI automation",
        "geography": "United States",
        "research_type": "Market Opportunity",
        "depth": "Standard",
        "instructions": "",
        "source_urls": [],
    }
    payload.update(overrides)
    return payload


def valid_brand_payload(**overrides):
    payload = {
        "brand_name": "Nexalyze",
        "company_profile": "Nexalyze builds AI operating systems for growth teams.",
        "mission": "Turn AI into repeatable growth workflows.",
        "brand_voice": "Strategic and practical.",
        "target_audience": "Founders and marketing leaders",
        "products_and_services": [
            {
                "name": "GrowthOS",
                "description": "AI growth operating system.",
                "audience": "SMB growth teams",
                "value": "Faster planning",
            }
        ],
    }
    payload.update(overrides)
    return payload


def create_brand():
    response = client.post("/api/v1/brands", json=valid_brand_payload())
    assert response.status_code == 201
    return response.json()


def create_research_run(**overrides):
    response = client.post("/api/v1/research/runs", json=valid_research_payload(**overrides))
    assert response.status_code == 201
    return response.json()


def mock_http_client(monkeypatch, handler):
    original_client = httpx.Client

    def client_factory(**kwargs):
        return original_client(
            transport=httpx.MockTransport(handler),
            timeout=kwargs.get("timeout"),
        )

    monkeypatch.setattr(httpx, "Client", client_factory)


def ollama_payload():
    return {
        "summary": "AI-generated synthesis. No live web research was performed.",
        "key_findings": [
            {"title": "Finding one", "detail": "Qualified finding detail for planning.", "importance": "high"},
            {"title": "Finding two", "detail": "Second qualified finding detail.", "importance": "medium"},
            {"title": "Finding three", "detail": "Third qualified finding detail.", "importance": "low"},
        ],
        "opportunities": ["Opportunity one", "Opportunity two"],
        "risks": ["Risk one"],
        "recommendations": ["Recommendation one", "Recommendation two"],
        "follow_up_questions": ["Question one?", "Question two?"],
    }


def test_successful_research_run():
    data = create_research_run()

    assert data["provider"] == "mock"
    assert data["brand_context_used"] is False
    assert data["topic"] == "AI automation for service businesses"
    assert len(data["key_findings"]) >= 3
    assert data["source_notes"][0]["url"] is None
    assert "No live web research performed" in data["source_notes"][0]["note"]


def test_research_validation_failure():
    response = client.post(
        "/api/v1/research/runs",
        json=valid_research_payload(topic="AI", research_type="Unsupported"),
    )

    assert response.status_code == 422


def test_brand_brain_injection():
    brand = create_brand()

    data = create_research_run(brand_id=brand["id"])

    assert data["brand_context_used"] is True
    assert "Brand Brain context was applied" in data["summary"]


def test_save_list_and_get_research_run():
    created = create_research_run()

    list_response = client.get("/api/v1/research/runs")
    get_response = client.get(f"/api/v1/research/runs/{created['id']}")

    assert list_response.status_code == 200
    assert list_response.json()["runs"][0]["id"] == created["id"]
    assert get_response.status_code == 200
    assert get_response.json()["id"] == created["id"]


def test_regenerate_research_run():
    created = create_research_run()

    response = client.post(f"/api/v1/research/runs/{created['id']}/regenerate")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["created_at"] == created["created_at"]


def test_delete_research_run():
    created = create_research_run()

    response = client.delete(f"/api/v1/research/runs/{created['id']}")

    assert response.status_code == 204
    assert client.get("/api/v1/research/runs").json()["runs"] == []


def test_corrupted_research_store_returns_controlled_error():
    Path(settings.research_store_path).write_text("{not-json", encoding="utf-8")

    response = client.get("/api/v1/research/runs")

    assert response.status_code == 500
    assert response.json()["detail"] == "Research storage is unavailable or corrupted."


def test_research_write_cleans_temporary_files():
    create_research_run()

    temporary_files = list(Path(settings.research_store_path).parent.glob("*.tmp"))

    assert temporary_files == []


def test_source_url_preserved_only_when_supplied():
    data = create_research_run(source_urls=["https://example.com/research-note"])

    assert data["source_notes"][0]["url"] == "https://example.com/research-note"
    assert "did not fetch or verify" in data["source_notes"][0]["note"]


def test_research_integrity_rules():
    data = create_research_run()
    joined = " ".join(
        [
            data["summary"],
            " ".join(finding["detail"] for finding in data["key_findings"]),
            " ".join(note["note"] for note in data["source_notes"]),
        ]
    )

    assert "No live web research" in joined
    assert "AI-generated synthesis" in joined
    assert "verified study" not in joined.lower()


def test_ollama_provider_success(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "ollama")
    monkeypatch.setattr(settings, "ollama_base_url", "http://ollama.test")
    monkeypatch.setattr(settings, "ollama_model", "qwen2.5:3b")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "http://ollama.test/api/generate"
        return httpx.Response(200, json={"response": json.dumps(ollama_payload())})

    mock_http_client(monkeypatch, handler)

    data = create_research_run()

    assert data["provider"] == "ollama"
    assert data["summary"].startswith("AI-generated synthesis")


def test_ollama_sparse_payload_is_normalized(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "ollama")
    monkeypatch.setattr(settings, "ollama_base_url", "http://ollama.test")

    sparse_payload = {
        "summary": "Sparse model response.",
        "key_findings": [{"title": "Signal", "detail": "A useful but thin signal."}],
        "opportunities": ["Pilot a focused research workflow."],
        "risks": [],
        "recommendations": ["Validate before publishing."],
        "follow_up_questions": ["Which buyers feel the pain most?"],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"response": json.dumps(sparse_payload)})

    mock_http_client(monkeypatch, handler)

    data = create_research_run()

    assert data["provider"] == "ollama"
    assert len(data["key_findings"]) == 3
    assert len(data["opportunities"]) == 2
    assert len(data["recommendations"]) == 2
    assert len(data["follow_up_questions"]) == 2


def test_ollama_timeout_uses_mock_fallback(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "ollama")

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timeout", request=request)

    mock_http_client(monkeypatch, handler)

    data = create_research_run()

    assert data["provider"] == "mock-fallback"


def test_ollama_connection_failure_uses_mock_fallback(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "ollama")

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection failed", request=request)

    mock_http_client(monkeypatch, handler)

    data = create_research_run()

    assert data["provider"] == "mock-fallback"


def test_malformed_ollama_json_uses_mock_fallback(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "ollama")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"response": "not-json"})

    mock_http_client(monkeypatch, handler)

    data = create_research_run()

    assert data["provider"] == "mock-fallback"
