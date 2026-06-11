import sqlite3
import pytest
import subprocess
import time
import socket
import os
from playwright.async_api import async_playwright

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

@pytest.fixture(scope="module")
def fastapi_server():
    port = 8002
    env = os.environ.copy()
    env["PYTHONPATH"] = "backend"
    env["DATABASE_URL"] = "backend/test_games.db"
    
    test_db = "backend/test_games.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    from backend.app.core import init_sqlite
    init_sqlite.init_database(test_db)
    
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO games (slug, title, title_ja) VALUES (?, ?, ?)",
        ("catan", "Catan", "カタン")
    )
    conn.commit()
    conn.close()
    
    process = subprocess.Popen(
        ["uv", "run", "python", "-m", "uvicorn", "backend.app.main:app", "--port", str(port)],
        env=env
    )
    
    for _ in range(30):
        if is_port_open(port):
            break
        time.sleep(0.5)
    else:
        process.terminate()
        raise RuntimeError("FastAPI server failed to start")
        
    yield f"http://127.0.0.1:{port}"
    
    process.terminate()
    process.wait()
    if os.path.exists(test_db):
        os.remove(test_db)

@pytest.mark.asyncio
async def test_category_5_multimedia(fastapi_server):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        request_context = await p.request.new_context(base_url=fastapi_server)
        
        artworks_data = [
            {"image_url": "https://example.com/catan1.jpg", "title": "Catan Box Art"},
            {"image_url": "https://example.com/catan2.jpg", "title": "Catan Board Setup"}
        ]
        resp = await request_context.post("/api/games/catan/artworks", data=artworks_data)
        assert resp.status == 200
        data = await resp.json()
        assert data["success"] is True
        
        resp = await request_context.get("/api/games/catan/artworks")
        assert resp.status == 200
        data = await resp.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0]["image_url"] == "https://example.com/catan1.jpg"
        assert data["data"][0]["title"] == "Catan Box Art"
        
        resp = await request_context.get("/api/games/catan/videos")
        assert resp.status == 200
        data = await resp.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
        assert "video_id" in data["data"][0]
        assert "title" in data["data"][0]
        
        pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
        resp = await request_context.get(f"/api/pdf/proxy?url={pdf_url}&page=1")
        assert resp.status == 200
        assert resp.headers.get("content-type") == "image/png"
        body = await resp.body()
        assert len(body) > 0
        
        await request_context.dispose()
        await browser.close()
