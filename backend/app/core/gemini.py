import json
import logging
from typing import Any

from playwright.async_api import async_playwright

from app.core.settings import settings

logger: logging.Logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self) -> None:
        self.api_key: str = str(settings.gemini_api_key)
        self.model: str = str(settings.gemini_model)

    async def generate_structured_json(self, prompt: str, api_key: str | None = None) -> dict[str, Any]:
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0,
                "response_mime_type": "application/json",
            },
        }
        key = api_key or self.api_key

        async with async_playwright() as p:
            request_context = await p.request.new_context(
                base_url="https://generativelanguage.googleapis.com", extra_http_headers={"x-goog-api-key": key}
            )

            resp = await request_context.post(f"/v1beta/{self.model}:generateContent", data=data)

            resp_json = await resp.json()
            await request_context.dispose()

        text = str(resp_json["candidates"][0]["content"]["parts"][0]["text"])
        # No more regex checks, assume clean JSON from the API as requested
        return json.loads(text)
