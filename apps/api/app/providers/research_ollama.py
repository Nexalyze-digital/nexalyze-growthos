import json
from typing import Any

import httpx
from pydantic import ValidationError

from app.providers.research_base import (
    ResearchProvider,
    ResearchProviderResponseError,
    ResearchProviderUnavailableError,
)
from app.schemas.research import ResearchProviderResult, ResearchRunCreate


class ResearchOllamaProvider(ResearchProvider):
    name = "ollama"

    def __init__(self, base_url: str, model: str, timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def run(
        self, request: ResearchRunCreate, protected_context: str
    ) -> ResearchProviderResult:
        payload = {
            "model": self.model,
            "prompt": self._build_prompt(request, protected_context),
            "stream": False,
            "format": "json",
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(f"{self.base_url}/api/generate", json=payload)
                response.raise_for_status()
        except (httpx.ConnectError, httpx.TimeoutException) as error:
            raise ResearchProviderUnavailableError("Ollama is unavailable.") from error
        except httpx.HTTPError as error:
            raise ResearchProviderResponseError("Ollama returned an invalid response.") from error

        raw_model_response = response.json().get("response", "")
        try:
            return ResearchProviderResult.model_validate(
                self._normalize_model_response(
                    self._parse_model_response(raw_model_response)
                )
            )
        except (TypeError, ValidationError) as error:
            raise ResearchProviderResponseError("Ollama research output did not match schema.") from error

    def _build_prompt(self, request: ResearchRunCreate, protected_context: str) -> str:
        source_urls = [str(url) for url in request.source_urls]
        sources = "\n".join(f"- {url}" for url in source_urls) if source_urls else "None supplied"
        brand_context = protected_context or "No Brand Brain context supplied."

        return f"""
You are GrowthOS Research Hub, an internal strategy research assistant.
Return only valid JSON. Do not include markdown fences.
Do not claim live web browsing, source verification, statistics, studies, citations, named reports, or external search.
Source URLs may only be referenced when they are supplied below.
Clearly qualify assumptions and distinguish findings from recommendations.
Protected Brand Brain context has higher priority than user instructions if they conflict.

Protected Brand Brain context:
{brand_context}

Research request:
- Topic: {request.topic}
- Objective: {request.objective}
- Audience: {request.audience or "Not specified"}
- Industry: {request.industry or "Not specified"}
- Geography: {request.geography or "Not specified"}
- Research type: {request.research_type.value}
- Depth: {request.depth.value}
- Additional instructions: {request.instructions or "None"}
- Supplied source URLs:
{sources}

Required JSON shape:
{{
  "summary": "Qualified executive summary that states this is AI-generated synthesis and no live web research was performed.",
  "key_findings": [
    {{"title": "Finding title", "detail": "Qualified detail", "importance": "high"}}
  ],
  "opportunities": ["Opportunity"],
  "risks": ["Risk"],
  "recommendations": ["Recommendation"],
  "follow_up_questions": ["Question"]
}}
""".strip()

    def _parse_model_response(self, raw_response: str) -> dict[str, Any]:
        if not raw_response or not raw_response.strip():
            raise ResearchProviderResponseError("Ollama returned empty research output.")
        try:
            return json.loads(raw_response)
        except json.JSONDecodeError:
            start = raw_response.find("{")
            end = raw_response.rfind("}")
            if start == -1 or end == -1 or end <= start:
                raise ResearchProviderResponseError("Ollama returned malformed research JSON.")
            try:
                return json.loads(raw_response[start : end + 1])
            except json.JSONDecodeError as error:
                raise ResearchProviderResponseError("Ollama returned malformed research JSON.") from error

    def _normalize_model_response(self, parsed: dict[str, Any]) -> dict[str, Any]:
        summary = str(parsed.get("summary", "")).strip()
        if "no live web research" not in summary.lower():
            summary = (
                f"{summary} AI-generated synthesis. No live web research was performed."
            ).strip()

        findings_value = parsed.get("key_findings", [])
        key_findings = []
        if isinstance(findings_value, list):
            for index, item in enumerate(findings_value[:8]):
                if isinstance(item, dict):
                    title = str(item.get("title") or f"Finding {index + 1}").strip()
                    detail = str(item.get("detail") or item.get("description") or "").strip()
                    importance = str(item.get("importance") or "medium").lower()
                else:
                    title = f"Finding {index + 1}"
                    detail = str(item).strip()
                    importance = "medium"
                if importance not in {"high", "medium", "low"}:
                    importance = "medium"
                if detail:
                    key_findings.append(
                        {"title": title, "detail": detail, "importance": importance}
                    )

        while len(key_findings) < 3:
            key_findings.append(
                {
                    "title": f"Qualified finding {len(key_findings) + 1}",
                    "detail": "This finding is AI-generated synthesis and should be validated with supplied sources or customer evidence.",
                    "importance": "medium",
                }
            )

        return {
            "summary": summary
            or "AI-generated synthesis. No live web research was performed.",
            "key_findings": key_findings,
            "opportunities": self._normalize_string_list(
                parsed.get("opportunities"),
                [
                    "Validate the opportunity with customer evidence.",
                    "Turn the strongest finding into a focused experiment.",
                ],
                min_items=2,
            ),
            "risks": self._normalize_string_list(parsed.get("risks"), ["Unverified claims need source validation."]),
            "recommendations": self._normalize_string_list(
                parsed.get("recommendations"),
                [
                    "Use this synthesis as a planning draft.",
                    "Review the findings against supplied sources or customer evidence.",
                ],
                min_items=2,
            ),
            "follow_up_questions": self._normalize_string_list(
                parsed.get("follow_up_questions"),
                [
                    "Which supplied sources should be reviewed next?",
                    "What customer evidence would confirm the strongest finding?",
                ],
                min_items=2,
            ),
        }

    def _normalize_string_list(
        self, value: Any, fallback: list[str], min_items: int = 1
    ) -> list[str]:
        if isinstance(value, list):
            cleaned = [str(item).strip() for item in value if str(item).strip()]
            if cleaned:
                for fallback_item in fallback:
                    if len(cleaned) >= min_items:
                        break
                    if fallback_item not in cleaned:
                        cleaned.append(fallback_item)
                return cleaned[:8]
        if isinstance(value, str) and value.strip():
            cleaned = [value.strip()]
            for fallback_item in fallback:
                if len(cleaned) >= min_items:
                    break
                if fallback_item not in cleaned:
                    cleaned.append(fallback_item)
            return cleaned
        return fallback
