from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect("backend/games.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/games/search")
async def search(q: str = "", limit: int = 20, offset: int = 0):
    conn = get_db()
    # Simplified search for verification
    query = "%" + q + "%"
    cursor = conn.execute("SELECT * FROM games WHERE title LIKE ? LIMIT ? OFFSET ?", (query, limit, offset))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"data": rows}

@app.get("/api/health")
async def health():
    return {"status": "ok"}
