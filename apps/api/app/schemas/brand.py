from datetime import datetime, timezone
from typing import Self
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BuyerPersona(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=2, max_length=120)
    role: str = Field(default="", max_length=160)
    goals: list[str] = Field(default_factory=list, max_length=12)
    pain_points: list[str] = Field(default_factory=list, max_length=12)
    buying_triggers: list[str] = Field(default_factory=list, max_length=12)


class ProductService(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=2, max_length=140)
    description: str = Field(default="", max_length=1000)
    audience: str = Field(default="", max_length=240)
    value: str = Field(default="", max_length=500)


class Competitor(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=2, max_length=140)
    website: HttpUrl | None = None
    positioning_notes: str = Field(default="", max_length=1000)


class CaseStudy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., min_length=2, max_length=180)
    summary: str = Field(default="", max_length=1500)
    outcome: str = Field(default="", max_length=500)


class BrandBrainBase(BaseModel):
    company_profile: str = Field(default="", max_length=3000)
    brand_name: str = Field(..., min_length=2, max_length=140)
    mission: str = Field(default="", max_length=1000)
    vision: str = Field(default="", max_length=1000)
    core_values: list[str] = Field(default_factory=list, max_length=20)
    products_and_services: list[ProductService] = Field(default_factory=list, max_length=30)
    industry: str = Field(default="", max_length=140)
    target_audience: str = Field(default="", max_length=1000)
    icp: str = Field(default="", max_length=1500)
    buyer_personas: list[BuyerPersona] = Field(default_factory=list, max_length=20)
    competitors: list[Competitor] = Field(default_factory=list, max_length=30)
    brand_voice: str = Field(default="", max_length=1000)
    tone_guidelines: str = Field(default="", max_length=1000)
    writing_style: str = Field(default="", max_length=1000)
    value_propositions: list[str] = Field(default_factory=list, max_length=20)
    proof_points: list[str] = Field(default_factory=list, max_length=20)
    case_studies: list[CaseStudy] = Field(default_factory=list, max_length=20)
    website_urls: list[HttpUrl] = Field(default_factory=list, max_length=20)
    social_media_urls: list[HttpUrl] = Field(default_factory=list, max_length=20)
    preferred_ctas: list[str] = Field(default_factory=list, max_length=20)
    preferred_hashtags: list[str] = Field(default_factory=list, max_length=30)
    forbidden_phrases: list[str] = Field(default_factory=list, max_length=50)
    preferred_terminology: list[str] = Field(default_factory=list, max_length=50)
    languages: list[str] = Field(default_factory=list, max_length=20)
    regional_preferences: list[str] = Field(default_factory=list, max_length=20)

    @field_validator(
        "core_values",
        "value_propositions",
        "proof_points",
        "preferred_ctas",
        "preferred_hashtags",
        "forbidden_phrases",
        "preferred_terminology",
        "languages",
        "regional_preferences",
    )
    @classmethod
    def clean_string_list(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value if item and item.strip()]
        return list(dict.fromkeys(cleaned))

    @model_validator(mode="after")
    def require_meaningful_brand_context(self) -> Self:
        if not any(
            [
                self.company_profile.strip(),
                self.mission.strip(),
                self.brand_voice.strip(),
                self.target_audience.strip(),
                self.icp.strip(),
                self.products_and_services,
            ]
        ):
            raise ValueError(
                "Brand Brain requires at least one profile, mission, voice, audience, ICP, or product/service detail."
            )
        return self


class BrandBrainCreate(BrandBrainBase):
    pass


class BrandBrainUpdate(BrandBrainBase):
    pass


class BrandBrain(BrandBrainBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class BrandBrainList(BaseModel):
    brands: list[BrandBrain]


class BrandContextSummary(BaseModel):
    brand_id: str | None = None
    brand_name: str | None = None
    context: str = ""
    applied: bool = False
