from app.providers.research_base import ResearchProvider
from app.schemas.research import (
    FindingImportance,
    ResearchFinding,
    ResearchProviderResult,
    ResearchRunCreate,
)


class ResearchMockProvider(ResearchProvider):
    name = "mock"

    def run(
        self, request: ResearchRunCreate, protected_context: str
    ) -> ResearchProviderResult:
        context_note = (
            " Brand Brain context was applied to keep the synthesis aligned."
            if protected_context
            else ""
        )
        scope = f"{request.research_type.value.lower()} for {request.topic}"
        audience = request.audience or "the intended audience"
        geography = request.geography or "the selected market"

        return ResearchProviderResult(
            summary=(
                f"This is AI-generated synthesis for {scope}. No live web research "
                f"or source verification was performed.{context_note} The safest "
                f"interpretation is that {audience} need clearer evidence, sharper "
                f"positioning, and practical next steps in {geography}."
            ),
            key_findings=[
                ResearchFinding(
                    title="Demand signal needs qualification",
                    detail=(
                        f"{request.topic} appears useful as a strategic theme, but "
                        "GrowthOS should treat this as an assumption until validated "
                        "with customer conversations or supplied sources."
                    ),
                    importance=FindingImportance.high,
                ),
                ResearchFinding(
                    title="Positioning clarity is the immediate lever",
                    detail=(
                        f"For {audience}, the strongest early research angle is to "
                        "separate urgent pain points from general interest."
                    ),
                    importance=FindingImportance.medium,
                ),
                ResearchFinding(
                    title="Source confidence is intentionally limited",
                    detail=(
                        "This run did not browse the live web, call external search, "
                        "or verify third-party statistics. Treat findings as a "
                        "planning draft."
                    ),
                    importance=FindingImportance.high,
                ),
            ],
            opportunities=[
                f"Create a focused research brief around {request.topic}.",
                f"Interview {audience} to validate the highest-friction workflow.",
                "Convert validated findings into Content Studio prompts and offers.",
            ],
            risks=[
                "Unverified claims can overstate market certainty.",
                "Competitor or trend conclusions need supplied sources before publication.",
            ],
            recommendations=[
                "Label this output as AI-generated synthesis in internal notes.",
                "Collect real customer evidence before using findings in sales collateral.",
                "Use Brand Brain terminology when turning findings into content.",
            ],
            follow_up_questions=[
                f"What proof would make {request.topic} credible to {audience}?",
                "Which assumptions should be validated before publishing?",
                "What supplied sources should be added to the next research run?",
            ],
        )
