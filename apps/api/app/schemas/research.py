from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ResearchType(str, Enum):
    market_opportunity = "Market Opportunity"
    competitor_analysis = "Competitor Analysis"
    content_opportunity = "Content Opportunity"
    industry_trends = "Industry Trends"
    customer_pain_points = "Customer Pain Points"
    strategic_research = "Strategic Research"


class ResearchDepth(str, Enum):
    quick = "Quick"
    standard = "Standard"
    deep = "Deep"


class FindingImportance(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class ResearchFinding(BaseModel):
    title: str = Field(..., min_length=2, max_length=180)
    detail: str = Field(..., min_length=10, max_length=1500)
    importance: FindingImportance = FindingImportance.medium


class SourceNote(BaseModel):
    label: str = Field(..., min_length=2, max_length=180)
    url: HttpUrl | None = None
    note: str = Field(..., min_length=10, max_length=500)


class ResearchRunCreate(BaseModel):
    topic: str = Field(..., min_length=3, max_length=300)
    objective: str = Field(..., min_length=3, max_length=1000)
    audience: str = Field(default="", max_length=500)
    industry: str = Field(default="", max_length=200)
    geography: str = Field(default="", max_length=200)
    research_type: ResearchType
    depth: ResearchDepth
    instructions: str = Field(default="", max_length=2000)
    brand_id: str | None = Field(default=None, max_length=120)
    source_urls: list[HttpUrl] = Field(default_factory=list, max_length=10)

    @field_validator("source_urls")
    @classmethod
    def dedupe_source_urls(cls, value: list[HttpUrl]) -> list[HttpUrl]:
        seen = set()
        deduped = []
        for url in value:
            normalized = str(url)
            if normalized not in seen:
                seen.add(normalized)
                deduped.append(url)
        return deduped


class ResearchProviderResult(BaseModel):
    summary: str = Field(..., min_length=20, max_length=3000)
    key_findings: list[ResearchFinding] = Field(..., min_length=3, max_length=8)
    opportunities: list[str] = Field(..., min_length=2, max_length=8)
    risks: list[str] = Field(..., min_length=1, max_length=8)
    recommendations: list[str] = Field(..., min_length=2, max_length=8)
    follow_up_questions: list[str] = Field(..., min_length=2, max_length=8)


class ResearchRun(ResearchRunCreate, ResearchProviderResult):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_notes: list[SourceNote] = Field(default_factory=list, min_length=1, max_length=12)
    provider: str
    brand_context_used: bool = False
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ResearchRunList(BaseModel):
    runs: list[ResearchRun]
