import sqlite3

def get_connection():
    return sqlite3.connect("backend/games.db")

def init_fts():
    conn = get_connection()
    conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS games_fts USING fts5(title, description, content='games', content_rowid='id')")
    conn.commit()
    conn.close()

def search_games(query, limit=100, offset=0):
    conn = get_connection()
    # FTS5 search
    cursor = conn.execute(
        "SELECT g.* FROM games g JOIN games_fts f ON g.id = f.rowid WHERE games_fts MATCH ? LIMIT ? OFFSET ?",
        (query, limit, offset)
    )
    results = cursor.fetchall()
    conn.close()
    return results

# Initialize FTS5 on startup
init_fts()
