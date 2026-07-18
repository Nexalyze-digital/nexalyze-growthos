from app.providers.base import ContentProvider
from app.schemas.content import ContentGenerationRequest, ContentGenerationResponse


class MockContentProvider(ContentProvider):
    name = "mock"

    def generate(
        self, request: ContentGenerationRequest
    ) -> ContentGenerationResponse:
        title = self._title(request)
        content = self._content(request)
        hashtags = self._hashtags(request.topic)

        return ContentGenerationResponse(
            title=title,
            content=content,
            hashtags=hashtags,
            platform=request.platform,
            tone=request.tone,
            provider=self.name,
        )

    def _title(self, request: ContentGenerationRequest) -> str:
        return f"{request.topic}: A {request.goal.value} Playbook"

    def _content(self, request: ContentGenerationRequest) -> str:
        context = (
            f"\n\nContext to apply: {request.instructions.strip()}"
            if request.instructions
            else ""
        )
        angle = (
            f"{request.audience.value} need a practical way to turn "
            f"{request.topic} into repeatable growth momentum."
        )

        platform_templates = {
            "LinkedIn": (
                f"{angle}\n\n"
                f"The opportunity is not another isolated experiment. It is a "
                f"clear operating rhythm: define the goal, create reusable "
                f"inputs, review the output, and keep improving the system.\n\n"
                f"For {request.goal.value.lower()}, the strongest move is to "
                f"connect strategy with execution so every content cycle gets "
                f"faster, sharper, and easier to measure.{context}\n\n"
                f"Start small, document what works, and make the workflow part "
                f"of the team's weekly cadence."
            ),
            "X": (
                f"{request.topic} is useful when it becomes an operating habit, "
                f"not a side experiment. For {request.audience.value}, the win "
                f"is simple: clearer inputs, faster drafts, better review loops, "
                f"and stronger {request.goal.value.lower()}.{context}"
            ),
            "Instagram": (
                f"{request.topic} can turn scattered ideas into a cleaner growth "
                f"system.\n\n"
                f"For {request.audience.value}: make the workflow visible, keep "
                f"the message focused, and use each draft to teach the next one "
                f"what better looks like.{context}\n\n"
                f"Save this for your next content planning sprint."
            ),
            "Facebook": (
                f"If {request.topic} has felt too complex, start with the parts "
                f"your team repeats every week.\n\n"
                f"{request.audience.value} can use a simple process to plan, "
                f"draft, review, and improve content without losing the human "
                f"voice behind the brand.{context}\n\n"
                f"What is one workflow you would automate first?"
            ),
        }

        tone_prefix = {
            "Professional": "A practical perspective:",
            "Executive": "The strategic takeaway:",
            "Conversational": "Here is the simple version:",
            "Bold": "The old way is too slow:",
            "Educational": "A useful framework:",
        }[request.tone.value]

        return f"{tone_prefix}\n\n{platform_templates[request.platform.value]}"

    def _hashtags(self, topic: str) -> list[str]:
        words = [
            word.strip(".,:;!?()[]{}").title()
            for word in topic.split()
            if len(word.strip(".,:;!?()[]{}")) > 3
        ]
        topic_tags = [f"#{word}" for word in words[:2]]
        tags = topic_tags + ["#AI", "#GrowthOS", "#ContentStrategy"]
        unique_tags = list(dict.fromkeys(tags))
        return unique_tags[:5]
