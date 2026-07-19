from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api.routes import health as health_route
from app.core.config import settings
from app.providers.ollama import OllamaContentProvider
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_brand_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "brand_store_path", str(tmp_path / "brands.json"))
    yield


def valid_payload(**overrides):
    payload = {
        "topic": "AI automation for small businesses",
        "platform": "LinkedIn",
        "audience": "CEOs",
        "goal": "Lead Generation",
        "tone": "Professional",
        "instructions": "",
    }
    payload.update(overrides)
    return payload


def mock_http_client(monkeypatch, handler):
    original_client = httpx.Client

    def client_factory(**kwargs):
        return original_client(
            transport=httpx.MockTransport(handler),
            timeout=kwargs.get("timeout"),
        )

    monkeypatch.setattr(httpx, "Client", client_factory)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "growthos-api"
    assert data["version"] == "0.1.0"
    assert "ai_provider" in data
    assert "ollama_reachable" in data


def test_successful_content_generation():
    response = client.post("/api/v1/content/generate", json=valid_payload())

    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "LinkedIn"
    assert data["tone"] == "Professional"
    assert data["provider"] == "mock"
    assert len(data["hashtags"]) >= 3
    assert "AI automation" in data["title"]


def test_invalid_short_topic():
    response = client.post(
        "/api/v1/content/generate", json=valid_payload(topic="AI")
    )

    assert response.status_code == 422


def test_platform_specific_generation():
    response = client.post(
        "/api/v1/content/generate", json=valid_payload(platform="X")
    )

    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "X"
    assert len(data["content"]) < 320


def test_instructions_are_accepted():
    response = client.post(
        "/api/v1/content/generate",
        json=valid_payload(instructions="Mention weekly planning."),
    )

    assert response.status_code == 200
    assert "Mention weekly planning." in response.json()["content"]


def test_provider_field_in_api_response():
    response = client.post("/api/v1/content/generate", json=valid_payload())

    assert response.status_code == 200
    assert response.json()["provider"] in {"mock", "ollama", "mock-fallback"}


def test_ollama_provider_success(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "ollama")
    monkeypatch.setattr(settings, "ai_fallback_provider", "mock")
    monkeypatch.setattr(settings, "ollama_base_url", "http://ollama.test")
    monkeypatch.setattr(settings, "ollama_model", "qwen2.5:3b")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "http://ollama.test/api/generate"
        return httpx.Response(
            200,
            json={
                "response": (
                    '{"title":"Ollama title","content":"Ollama content",'
                    '"hashtags":["#AI","#GrowthOS","#LocalAI"]}'
                )
            },
        )

    mock_http_client(monkeypatch, handler)

    response = client.post("/api/v1/content/generate", json=valid_payload())

    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "ollama"
    assert data["title"] == "Ollama title"

    monkeypatch.setattr(settings, "ai_provider", "mock")


def test_ollama_connection_failure_uses_mock_fallback(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "ollama")
    monkeypatch.setattr(settings, "ai_fallback_provider", "mock")

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection failed", request=request)

    mock_http_client(monkeypatch, handler)

    response = client.post("/api/v1/content/generate", json=valid_payload())

    assert response.status_code == 200
    assert response.json()["provider"] == "mock-fallback"

    monkeypatch.setattr(settings, "ai_provider", "mock")


def test_ollama_timeout_uses_mock_fallback(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "ollama")
    monkeypatch.setattr(settings, "ai_fallback_provider", "mock")

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timeout", request=request)

    mock_http_client(monkeypatch, handler)

    response = client.post("/api/v1/content/generate", json=valid_payload())

    assert response.status_code == 200
    assert response.json()["provider"] == "mock-fallback"

    monkeypatch.setattr(settings, "ai_provider", "mock")


def test_malformed_model_output_uses_mock_fallback(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "ollama")
    monkeypatch.setattr(settings, "ai_fallback_provider", "mock")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"response": "not-json"})

    mock_http_client(monkeypatch, handler)

    response = client.post("/api/v1/content/generate", json=valid_payload())

    assert response.status_code == 200
    assert response.json()["provider"] == "mock-fallback"

    monkeypatch.setattr(settings, "ai_provider", "mock")


def test_ollama_provider_extracts_json_from_wrapped_response():
    provider = OllamaContentProvider(
        base_url="http://ollama.test",
        model="qwen2.5:3b",
        timeout_seconds=1,
    )

    parsed = provider._parse_model_response(
        'Here is JSON: {"title":"T","content":"C","hashtags":["#A","#B","#C"]}'
    )

    assert parsed["title"] == "T"


def test_ollama_provider_normalizes_parseable_model_output():
    provider = OllamaContentProvider(
        base_url="http://ollama.test",
        model="llama3.2:latest",
        timeout_seconds=1,
    )

    normalized = provider._normalize_model_response(
        {
            "title": "Title",
            "content": ["First paragraph", "Second paragraph"],
            "hashtags": "AI, GrowthOS",
        }
    )

    assert normalized == {
        "title": "Title",
        "content": "First paragraph\n\nSecond paragraph",
        "hashtags": ["#AI", "#GrowthOS", "#ContentStrategy"],
    }


def test_health_when_ollama_available(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "ollama")
    monkeypatch.setattr(health_route, "is_ollama_reachable", lambda base_url: True)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["ai_provider"] == "ollama"
    assert response.json()["ollama_reachable"] is True

    monkeypatch.setattr(settings, "ai_provider", "mock")


def test_health_when_ollama_unavailable(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "ollama")
    monkeypatch.setattr(health_route, "is_ollama_reachable", lambda base_url: False)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["ai_provider"] == "ollama"
    assert response.json()["ollama_reachable"] is False

    monkeypatch.setattr(settings, "ai_provider", "mock")
