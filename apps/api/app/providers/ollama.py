import json
from typing import Any

import httpx
from pydantic import ValidationError

from app.providers.base import (
    ContentProvider,
    ProviderResponseError,
    ProviderUnavailableError,
)
from app.schemas.content import ContentGenerationRequest, ContentGenerationResponse


class OllamaContentProvider(ContentProvider):
    name = "ollama"

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def generate(
        self, request: ContentGenerationRequest
    ) -> ContentGenerationResponse:
        payload = {
            "model": self.model,
            "prompt": self._build_prompt(request),
            "stream": False,
            "format": "json",
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
        except (httpx.ConnectError, httpx.TimeoutException) as error:
            raise ProviderUnavailableError("Ollama is unavailable.") from error
        except httpx.HTTPError as error:
            raise ProviderResponseError("Ollama returned an invalid response.") from error

        data = response.json()
        raw_model_response = data.get("response", "")
        parsed = self._normalize_model_response(
            self._parse_model_response(raw_model_response)
        )

        try:
            return ContentGenerationResponse(
                title=parsed["title"],
                content=parsed["content"],
                hashtags=parsed["hashtags"],
                platform=request.platform,
                tone=request.tone,
                provider=self.name,
            )
        except (KeyError, TypeError, ValidationError) as error:
            raise ProviderResponseError("Ollama response did not match schema.") from error

    def _build_prompt(self, request: ContentGenerationRequest) -> str:
        instructions = request.instructions.strip() if request.instructions else "None"

        return f"""
You are GrowthOS, a business content generation assistant.
Return only valid JSON. Do not include markdown fences.
Do not claim live research was performed.

Create a social post using these inputs:
- Topic: {request.topic}
- Platform: {request.platform.value}
- Audience: {request.audience.value}
- Goal: {request.goal.value}
- Tone: {request.tone.value}
- Additional instructions: {instructions}

Platform rules:
- LinkedIn: professional, structured, multi-paragraph.
- X: concise and within a practical post length.
- Instagram: caption-led and visually engaging.
- Facebook: conversational and community-oriented.

Required JSON shape:
{{
  "title": "Short title",
  "content": "Post body with paragraphs when appropriate",
  "hashtags": ["#TagOne", "#TagTwo", "#TagThree"]
}}
""".strip()

    def _parse_model_response(self, raw_response: str) -> dict[str, Any]:
        if not raw_response or not raw_response.strip():
            raise ProviderResponseError("Ollama returned empty content.")

        try:
            return json.loads(raw_response)
        except json.JSONDecodeError:
            extracted = self._extract_json_object(raw_response)
            if extracted is None:
                raise ProviderResponseError("Ollama returned malformed JSON.")
            try:
                return json.loads(extracted)
            except json.JSONDecodeError as error:
                raise ProviderResponseError("Ollama returned malformed JSON.") from error

    def _extract_json_object(self, raw_response: str) -> str | None:
        start = raw_response.find("{")
        end = raw_response.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        return raw_response[start : end + 1]

    def _normalize_model_response(self, parsed: dict[str, Any]) -> dict[str, Any]:
        title = str(parsed.get("title", "")).strip()
        content_value = parsed.get("content", "")
        hashtags_value = parsed.get("hashtags", [])

        if isinstance(content_value, list):
            content = "\n\n".join(str(item).strip() for item in content_value if item)
        else:
            content = str(content_value).strip()

        if isinstance(hashtags_value, str):
            raw_hashtags = hashtags_value.replace(",", " ").split()
        elif isinstance(hashtags_value, list):
            raw_hashtags = [str(item).strip() for item in hashtags_value]
        else:
            raw_hashtags = []

        hashtags = []
        for hashtag in raw_hashtags:
            if not hashtag:
                continue
            normalized = hashtag if hashtag.startswith("#") else f"#{hashtag}"
            hashtags.append(normalized.replace(" ", ""))

        unique_hashtags = list(dict.fromkeys(hashtags))

        for fallback_tag in ["#AI", "#GrowthOS", "#ContentStrategy"]:
            if len(unique_hashtags) >= 3:
                break
            if fallback_tag not in unique_hashtags:
                unique_hashtags.append(fallback_tag)

        unique_hashtags = unique_hashtags[:5]

        return {
            "title": title,
            "content": content,
            "hashtags": unique_hashtags,
        }


def is_ollama_reachable(base_url: str, timeout_seconds: float = 2) -> bool:
    try:
        with httpx.Client(timeout=timeout_seconds) as client:
            response = client.get(f"{base_url.rstrip('/')}/api/tags")
            response.raise_for_status()
    except httpx.HTTPError:
        return False
    return True
