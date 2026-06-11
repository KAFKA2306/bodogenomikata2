import sqlite3
import asyncio
import os
import sys

# Ensure backend is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.services.bgg_fetcher import BGGFetcher
from app.utils import map_bgg_to_games_schema

async def enrich_games(db_path):
    fetcher = BGGFetcher()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get games with missing fields
    cursor.execute("""
        SELECT id, title FROM games 
        WHERE description IS NULL OR bgg_url IS NULL OR play_time IS NULL
        LIMIT 100
    """)
    rows = cursor.fetchall()
    
    if not rows:
        print("No games to enrich.")
        conn.close()
        return

    print(f"Found {len(rows)} games to enrich.")
    
    for row in rows:
        game_id, title = row
        print(f"Enriching: {title}")
        
        try:
            bgg_id = await fetcher.search_game(title)
            if bgg_id:
                bgg_data = await fetcher.fetch_game_by_id(bgg_id)
                if bgg_data:
                    schema_data = map_bgg_to_games_schema(bgg_data)
                    
                    # Update DB
                    cursor.execute("""
                        UPDATE games SET 
                            description = ?, 
                            bgg_url = ?, 
                            play_time = ? 
                        WHERE id = ?
                    """, (
                        schema_data.get('description'), 
                        schema_data.get('bgg_url'), 
                        schema_data.get('play_time'), 
                        game_id
                    ))
                    conn.commit()
                    print(f"Updated: {title}")
                else:
                    print(f"Failed to fetch data for: {title}")
            else:
                print(f"Game not found on BGG: {title}")
        
        except Exception as e:
            print(f"Error enriching {title}: {e}")
        
        await asyncio.sleep(1) # Be nice to BGG
        
    conn.close()
    print("Enrichment batch complete.")

if __name__ == "__main__":
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../games.db'))
    asyncio.run(enrich_games(db_path))
