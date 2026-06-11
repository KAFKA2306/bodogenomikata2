from app.core import sqlite_client

def calculate_popularity(game: dict) -> float:
    # Formula: view_count * 0.3 + search_count * 0.2 + avg_rating * 5.0
    slug = game.get("slug")
    if not slug:
        return 0.0
    
    avg_rating = sqlite_client.get_average_rating(slug)
    view_count = game.get("view_count") or 0
    search_count = game.get("search_count") or 0
    
    return (view_count * 0.3) + (search_count * 0.2) + (avg_rating * 5.0)

def get_top_rated_games(limit: int = 20) -> list[dict]:
    # Fetch a sufficient number of games to rank
    all_games = sqlite_client.list_games(limit=1000)
    
    scored_games = []
    for game in all_games:
        # Calculate score
        score = calculate_popularity(game)
        game["popularity_score"] = score
        scored_games.append(game)
        
    # Sort descending
    scored_games.sort(key=lambda x: x["popularity_score"], reverse=True)
    
    return scored_games[:limit]
