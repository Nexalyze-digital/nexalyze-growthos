from enum import Enum

from pydantic import BaseModel, Field


class Platform(str, Enum):
    linkedin = "LinkedIn"
    x = "X"
    instagram = "Instagram"
    facebook = "Facebook"


class Audience(str, Enum):
    ceos = "CEOs"
    founders = "Founders"
    marketing_leaders = "Marketing Leaders"
    smes = "SMEs"
    general_business = "General Business Audience"


class Goal(str, Enum):
    lead_generation = "Lead Generation"
    brand_awareness = "Brand Awareness"
    thought_leadership = "Thought Leadership"
    engagement = "Engagement"
    education = "Education"


class Tone(str, Enum):
    professional = "Professional"
    executive = "Executive"
    conversational = "Conversational"
    bold = "Bold"
    educational = "Educational"


class ContentGenerationRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=300)
    platform: Platform
    audience: Audience
    goal: Goal
    tone: Tone
    instructions: str | None = Field(default=None, max_length=2000)


class ContentGenerationResponse(BaseModel):
    title: str
    content: str
    hashtags: list[str] = Field(..., min_length=3, max_length=5)
    platform: Platform
    tone: Tone
    provider: str
