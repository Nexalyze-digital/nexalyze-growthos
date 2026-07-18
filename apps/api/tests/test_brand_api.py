from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_brand_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "brand_store_path", str(tmp_path / "brands.json"))
    monkeypatch.setattr(settings, "ai_provider", "mock")
    yield


def valid_brand_payload(**overrides):
    payload = {
        "company_profile": "Nexalyze builds AI operating systems for growth teams.",
        "brand_name": "Nexalyze",
        "mission": "Help teams turn AI into repeatable growth workflows.",
        "vision": "A practical AI command center for every growth team.",
        "core_values": ["Clarity", "Velocity", "Trust"],
        "products_and_services": [
            {
                "name": "GrowthOS",
                "description": "An AI growth operating system.",
                "audience": "SMB growth teams",
                "value": "Faster planning and execution",
            }
        ],
        "industry": "AI automation",
        "target_audience": "Founders and marketing leaders",
        "icp": "Service businesses ready to operationalize AI.",
        "buyer_personas": [
            {
                "name": "Growth Founder",
                "role": "Founder",
                "goals": ["Generate pipeline"],
                "pain_points": ["Manual content workflows"],
                "buying_triggers": ["Need repeatable growth"],
            }
        ],
        "competitors": [
            {
                "name": "Generic AI Tool",
                "website": "https://example.com",
                "positioning_notes": "Broad assistant, not operating system.",
            }
        ],
        "brand_voice": "Strategic, direct, and useful.",
        "tone_guidelines": "Confident without hype.",
        "writing_style": "Short paragraphs and concrete examples.",
        "value_propositions": ["AI workflows that compound"],
        "proof_points": ["Validated local AI integration"],
        "case_studies": [
            {
                "title": "Content Studio",
                "summary": "Built an end-to-end AI content workflow.",
                "outcome": "Validated generation and fallback.",
            }
        ],
        "website_urls": ["https://nexalyze.com"],
        "social_media_urls": ["https://www.linkedin.com/company/nexalyze"],
        "preferred_ctas": ["Book a growth systems audit"],
        "preferred_hashtags": ["#GrowthOS", "#AIAutomation"],
        "forbidden_phrases": ["game changer"],
        "preferred_terminology": ["operating system", "growth workflows"],
        "languages": ["English"],
        "regional_preferences": ["United States"],
    }
    payload.update(overrides)
    return payload


def create_brand(**overrides):
    response = client.post("/api/v1/brands", json=valid_brand_payload(**overrides))
    assert response.status_code == 201
    return response.json()


def test_create_and_list_brand_brain_profile():
    created = create_brand()

    response = client.get("/api/v1/brands")

    assert response.status_code == 200
    brands = response.json()["brands"]
    assert len(brands) == 1
    assert brands[0]["id"] == created["id"]
    assert brands[0]["brand_name"] == "Nexalyze"


def test_update_brand_brain_profile():
    created = create_brand()

    response = client.put(
        f"/api/v1/brands/{created['id']}",
        json=valid_brand_payload(brand_name="Nexalyze GrowthOS"),
    )

    assert response.status_code == 200
    assert response.json()["brand_name"] == "Nexalyze GrowthOS"
    assert response.json()["id"] == created["id"]


def test_delete_brand_brain_profile():
    created = create_brand()

    response = client.delete(f"/api/v1/brands/{created['id']}")

    assert response.status_code == 204
    assert client.get("/api/v1/brands").json()["brands"] == []


def test_brand_validation_rejects_empty_context():
    payload = valid_brand_payload(
        company_profile="",
        mission="",
        brand_voice="",
        target_audience="",
        icp="",
        products_and_services=[],
    )

    response = client.post("/api/v1/brands", json=payload)

    assert response.status_code == 422


def test_content_generation_injects_brand_brain_context():
    create_brand()

    response = client.post(
        "/api/v1/content/generate",
        json={
            "topic": "AI content operations",
            "platform": "LinkedIn",
            "audience": "Founders",
            "goal": "Thought Leadership",
            "tone": "Executive",
            "instructions": "Mention the weekly planning loop.",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["brand_context_applied"] is True
    assert data["brand_name"] == "Nexalyze"
    assert "Nexalyze" in data["content"]
    assert "weekly planning loop" in data["content"]
