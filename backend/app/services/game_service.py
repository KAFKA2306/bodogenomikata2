from datetime import datetime, timezone
from typing import Any

from app.core import sqlite_client
from app.core.gemini import GeminiClient
from app.core.settings import settings
from app.models import GeneratedGameMetadata

_gemini = GeminiClient()


async def generate_metadata(query: str, context: str | None = None) -> dict[str, Any]:
    # Success path only: assume context or search results exist
    rows = sqlite_client.search_games(query)
    context = context or "\n".join(f"{r['title']}: {r['summary']}" for r in rows[:3])

    prompt = f"Generate JSON for: {query}\nContext: {context}"
    result = await _gemini.generate_structured_json(prompt, api_key=settings.gemini_api_key)
    validated = GeneratedGameMetadata.model_validate(result)

    data = validated.model_dump()
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    return sqlite_client.upsert_game(data)


class GameService:
    async def get_game_by_slug(self, slug: str) -> dict[str, Any]:
        return sqlite_client.get_game_by_slug(slug)

    async def update_game_manual(self, slug: str, data: dict[str, Any]) -> dict[str, Any]:
        original = sqlite_client.get_game_by_slug(slug)
        original.update(data)
        return sqlite_client.upsert_game(original)
