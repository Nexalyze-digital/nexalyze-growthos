from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.db.models import Draft, PublishingJob
from app.schemas.publishing import PublishingJobStatus, utc_now


@dataclass(frozen=True)
class PublishingProviderResult:
    status: PublishingJobStatus
    provider_post_id: str | None
    error_category: str | None
    summary: str
    published_at: datetime | None


class MockPublishingProvider:
    name = "mock"

    def publish(self, job: PublishingJob, draft: Draft, attempt_number: int, behavior: str) -> PublishingProviderResult:
        outcome = self._outcome(draft, behavior)
        platform_key = job.platform.lower().replace(" ", "-")
        if outcome == "success":
            return PublishingProviderResult(
                status=PublishingJobStatus.published,
                provider_post_id=f"mock-{platform_key}-{job.id[:8]}-{attempt_number}",
                error_category=None,
                summary=f"Mock {job.platform} provider accepted the draft.",
                published_at=utc_now(),
            )
        if outcome == "transient":
            return PublishingProviderResult(
                status=PublishingJobStatus.failed,
                provider_post_id=None,
                error_category="transient",
                summary=f"Mock {job.platform} provider returned a retryable error.",
                published_at=None,
            )
        return PublishingProviderResult(
            status=PublishingJobStatus.failed,
            provider_post_id=None,
            error_category="permanent",
            summary=f"Mock {job.platform} provider rejected the draft permanently.",
            published_at=None,
        )

    def _outcome(self, draft: Draft, behavior: str) -> str:
        if behavior == "success":
            return "success"
        if behavior == "transient_failure":
            return "transient"
        if behavior == "permanent_failure":
            return "permanent"
        content = f"{draft.title}\n{draft.body}".lower()
        if "[mock:transient]" in content:
            return "transient"
        if "[mock:permanent]" in content:
            return "permanent"
        return "success"
