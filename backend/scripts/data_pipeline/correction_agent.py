import sqlite3
import time

def fetch_missing_data(game_id):
    # API呼び出しシミュレーション (実際はBGG XML APIを叩く)
    print(f"CorrectionAgent: Fetching data for game ID {game_id} from BGG...")
    time.sleep(1) 
    return {"min_players": 2, "max_players": 4, "play_time": 60}

def correct_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # 欠損データを取得
    games = cursor.execute("SELECT id, bgg_id FROM games WHERE min_players IS NULL").fetchall()
    
    for g_id, bgg_id in games:
        data = fetch_missing_data(bgg_id)
        cursor.execute("UPDATE games SET min_players=?, max_players=?, play_time=? WHERE id=?", 
                       (data['min_players'], data['max_players'], data['play_time'], g_id))
        conn.commit()
    conn.close()
    print("CorrectionAgent: Database updated.")

if __name__ == "__main__":
    correct_database("backend/games.db")
