import pytest
from app.services.ranking_service import get_top_rated_games
from app.core import sqlite_client

@pytest.mark.asyncio
async def test_top_rated_games():
    # Insert some dummy games with different metrics
    sqlite_client.upsert_game({"slug": "game-1", "title": "Game 1", "view_count": 100, "search_count": 50})
    sqlite_client.upsert_game({"slug": "game-2", "title": "Game 2", "view_count": 200, "search_count": 10})
    sqlite_client.upsert_game({"slug": "game-3", "title": "Game 3", "view_count": 10, "search_count": 10})
    
    # Add reviews
    sqlite_client.upsert_user_review("game-1", "user1", 8.0, None)
    sqlite_client.upsert_user_review("game-2", "user2", 5.0, None)
    sqlite_client.upsert_user_review("game-3", "user3", 9.0, None)
    
    # Get top rated
    top_games = get_top_rated_games(limit=2)
    
    assert len(top_games) == 2
    # Verify rankings
    # game-1: (100 * 0.3) + (50 * 0.2) + (8.0 * 5.0) = 30 + 10 + 40 = 80
    # game-2: (200 * 0.3) + (10 * 0.2) + (5.0 * 5.0) = 60 + 2 + 25 = 87
    # game-3: (10 * 0.3) + (10 * 0.2) + (9.0 * 5.0) = 3 + 2 + 45 = 50
    # Expected order: game-2, game-1
    
    assert top_games[0]["slug"] == "game-2"
    assert top_games[1]["slug"] == "game-1"
