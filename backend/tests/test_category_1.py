import pytest
from app.routers import get_game_credits, get_game_expansions, sync_game
from app.core import sqlite_client

@pytest.mark.asyncio
async def test_database_credits_and_relations():
    # Insert some dummy game
    sqlite_client.upsert_game({
        "slug": "base-game",
        "title": "Base Game",
    })
    
    # Insert credits and expansions
    sqlite_client.upsert_game_credits_and_relations(
        game_slug="base-game",
        designers=[{"name": "Designer A", "bgg_id": 101, "slug": "designer-a"}],
        publishers=[{"name": "Publisher X", "bgg_id": 201, "slug": "publisher-x"}],
        expansions=[{"name": "Expansion One", "bgg_id": 901, "slug": "expansion-one"}],
        expands=[]
    )
    
    # Verify credits query
    credits = sqlite_client.get_game_credits("base-game")
    assert len(credits["designers"]) == 1
    assert credits["designers"][0]["name"] == "Designer A"
    assert credits["designers"][0]["slug"] == "designer-a"
    assert len(credits["publishers"]) == 1
    assert credits["publishers"][0]["name"] == "Publisher X"
    
    # Verify relationship query
    expansions = sqlite_client.get_game_expansions("base-game")
    assert len(expansions["expansions"]) == 1
    assert expansions["expansions"][0]["slug"] == "expansion-one"
    
    # Test credits endpoint function directly
    resp = await get_game_credits(slug="base-game")
    assert resp["success"] is True
    assert len(resp["data"]["designers"]) == 1
    assert resp["data"]["designers"][0]["name"] == "Designer A"

    # Test expansions endpoint function directly
    resp = await get_game_expansions(slug="base-game")
    assert resp["success"] is True
    assert len(resp["data"]["expansions"]) == 1
    assert resp["data"]["expansions"][0]["slug"] == "expansion-one"

@pytest.mark.asyncio
async def test_bgg_sync_by_id():
    # Sync Catan (BGG ID: 13)
    resp = await sync_game(bgg_id=13)
    assert resp["success"] is True
    assert resp["data"]["bgg_id"] == 13
    
    # Check if credits were populated
    slug = resp["data"]["slug"]
    credits = sqlite_client.get_game_credits(slug)
    assert len(credits["designers"]) > 0
    designer_names = [d["name"] for d in credits["designers"]]
    assert any("Klaus Teuber" in name for name in designer_names)
    
    # Check if publishers were populated
    assert len(credits["publishers"]) > 0
