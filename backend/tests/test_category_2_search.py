import pytest
from backend.app.core import sqlite_client

@pytest.fixture(autouse=True)
def populate_data():
    conn = sqlite_client.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM games")
    conn.commit()
    conn.close()

    sqlite_client.upsert_game({
        "slug": "catan",
        "title": "Catan",
        "title_ja": "カタン",
        "title_en": "Catan",
        "description": "A classic board game of trading and building.",
        "min_players": 3,
        "max_players": 4,
        "play_time": 90,
        "structured_data": {
            "mechanics": ["Dice Rolling", "Trading", "Network Building"]
        }
    })

    sqlite_client.upsert_game({
        "slug": "carcassonne",
        "title": "Carcassonne",
        "title_ja": "カルカソンヌ",
        "title_en": "Carcassonne",
        "description": "A tile-placement game where players draw and place tiles.",
        "min_players": 2,
        "max_players": 5,
        "play_time": 45,
        "structured_data": {
            "mechanics": ["Tile Placement", "Area Majority"]
        }
    })

    sqlite_client.upsert_game({
        "slug": "pandemic",
        "title": "Pandemic",
        "title_ja": "パンデミック",
        "title_en": "Pandemic",
        "description": "Cooperative game to stop global disease outbreaks.",
        "min_players": 2,
        "max_players": 4,
        "play_time": 45,
        "structured_data": {
            "mechanics": ["Cooperative Game", "Trading", "Action Points"]
        }
    })

def test_query_search():
    results = sqlite_client.search_games(query="カタン")
    assert len(results) == 1
    assert results[0]["slug"] == "catan"

    results = sqlite_client.search_games(query="Classic")
    assert len(results) == 1
    assert results[0]["slug"] == "catan"

def test_player_count_filtering():
    results = sqlite_client.search_games(min_players=3)
    assert len(results) == 1
    assert results[0]["slug"] == "catan"

    results = sqlite_client.search_games(max_players=4)
    assert len(results) == 2
    slugs = [r["slug"] for r in results]
    assert "catan" in slugs
    assert "pandemic" in slugs

def test_play_time_filtering():
    results = sqlite_client.search_games(play_time=50)
    assert len(results) == 2
    slugs = [r["slug"] for r in results]
    assert "carcassonne" in slugs
    assert "pandemic" in slugs

def test_mechanics_filtering():
    results = sqlite_client.search_games(mechanics=["Trading"])
    assert len(results) == 2
    slugs = [r["slug"] for r in results]
    assert "catan" in slugs
    assert "pandemic" in slugs

    results = sqlite_client.search_games(mechanics=["Trading", "Dice Rolling"])
    assert len(results) == 1
    assert results[0]["slug"] == "catan"

    results = sqlite_client.search_games(mechanics=["Farming"])
    assert len(results) == 0

def test_autocomplete():
    suggestions = sqlite_client.autocomplete_suggestions("Cat")
    assert len(suggestions) >= 1
    assert suggestions[0]["slug"] == "catan"

    suggestions = sqlite_client.autocomplete_suggestions("pan")
    assert len(suggestions) >= 1
    assert suggestions[0]["slug"] == "pandemic"
