import logging
from typing import Any

from app.core import sqlite_client
from app.services.bgg_fetcher import BGGFetcher
from app.utils import map_bgg_to_games_schema

logger = logging.getLogger("services.bgg_service")


class BGGService:
    def __init__(self):
        self.fetcher = BGGFetcher()

    async def fetch_and_upsert_game(self, game_id: int) -> dict[str, Any] | None:
        bgg_data = await self.fetcher.fetch_game_by_id(game_id)
        if not bgg_data:
            logger.warning(f"Failed to fetch game {game_id} from BGG API")
            return None

        schema_data = map_bgg_to_games_schema(bgg_data)
        logger.info(f"Mapped BGG data for game {game_id}: {schema_data}")

        result = sqlite_client.upsert_game(schema_data)
        logger.info(f"Successfully upserted game {game_id}")
        
        # Category 1: Upsert credits and relationships
        sqlite_client.upsert_game_credits_and_relations(
            game_slug=schema_data["slug"],
            designers=bgg_data.get("designers", []),
            publishers=bgg_data.get("publishers", []),
            expansions=bgg_data.get("expansions", []),
            expands=bgg_data.get("expands", [])
        )
        
        return result

    async def fetch_and_upsert_multiple(self, game_ids: list[int]) -> list[dict[str, Any] | None]:
        results = []
        for game_id in game_ids:
            result = await self.fetch_and_upsert_game(game_id)
            results.append(result)
        return results
