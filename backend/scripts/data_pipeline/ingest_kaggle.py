import sqlite3
import pandas as pd

def ingest_data(kaggle_db_path, target_db_path):
    print("Ingesting Kaggle data...")
    src_conn = sqlite3.connect(kaggle_db_path)
    df = pd.read_sql_query("SELECT * FROM BoardGames", src_conn)
    src_conn.close()
    
    # 正しいカラム名でマッピング
    mapping = {
        'details.name': 'title',
        'details.description': 'description',
        'details.yearpublished': 'published_year',
        'details.minplayers': 'min_players',
        'details.maxplayers': 'max_players',
        'details.playingtime': 'play_time',
        'details.minage': 'min_age'
    }
    
    # 必要な列のみ選択しリネーム
    subset = df[list(mapping.keys())].rename(columns=mapping)
    
    # ターゲットDBへ接続しインサート
    target_conn = sqlite3.connect(target_db_path)
    target_conn.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            published_year INTEGER,
            min_players INTEGER,
            max_players INTEGER,
            play_time INTEGER,
            min_age INTEGER
        )
    """)
    subset.to_sql('games', target_conn, if_exists='append', index=False)
    target_conn.close()
    print("Ingestion complete.")

if __name__ == "__main__":
    ingest_data("backend/scripts/data_pipeline/data/database.sqlite", "backend/games.db")
