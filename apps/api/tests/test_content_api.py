from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


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


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "growthos-api",
        "version": "0.1.0",
    }


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
