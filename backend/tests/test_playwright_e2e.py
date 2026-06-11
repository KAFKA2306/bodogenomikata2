import pytest
import subprocess
import time
import socket
from playwright.async_api import async_playwright
import os

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

@pytest.fixture(scope="module")
def fastapi_server():
    """本物のプロセスとしてFastAPIを起動します。"""
    port = 8001
    env = os.environ.copy()
    env["PYTHONPATH"] = "backend"
    
    # Force test database for the server process
    env["DATABASE_URL"] = "backend/test_games.db"
    
    process = subprocess.Popen(
        ["uv", "run", "python", "-m", "uvicorn", "backend.app.main:app", "--port", str(port)],
        env=env
    )
    
    # Wait for server to be ready
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

@pytest.mark.asyncio
async def test_health_check_playwright(fastapi_server):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        
        # Test /health
        resp = await page.goto(f"{fastapi_server}/health")
        assert resp.status == 200
        content = await resp.json()
        assert content == {"status": "ok"}
        
        await browser.close()

@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY is not set")
@pytest.mark.asyncio
async def test_sync_flow_playwright(fastapi_server):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # Request context for API testing
        request_context = await p.request.new_context(base_url=fastapi_server)
        
        # 1. Sync Catan (ID: 13)
        # Using post method of request_context
        resp = await request_context.post("/api/games/sync?bgg_id=13")
        assert resp.status == 200
        data = await resp.json()
        assert data["success"] is True
        slug = data["data"]["slug"]
        
        # 2. Get the synced game
        get_resp = await request_context.get(f"/api/games/{slug}")
        assert get_resp.status == 200
        get_data = await get_resp.json()
        assert get_data["data"]["bgg_id"] == 13
        
        await request_context.dispose()
        await browser.close()

@pytest.mark.asyncio
async def test_search_and_autocomplete_endpoints(fastapi_server):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        request_context = await p.request.new_context(base_url=fastapi_server)

        from backend.app.core import sqlite_client
        sqlite_client.upsert_game({
            "slug": "catan",
            "title": "Catan",
            "title_ja": "カタン",
            "title_en": "Catan",
            "description": "Trading and building.",
            "min_players": 3,
            "max_players": 4,
            "play_time": 90,
            "structured_data": {
                "mechanics": ["Dice Rolling", "Trading"]
            }
        })

        resp = await request_context.get("/api/games/search?q=catan&min_players=3&mechanics=Trading")
        assert resp.status == 200
        data = await resp.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["slug"] == "catan"

        resp = await request_context.get("/api/games/autocomplete?q=cat")
        assert resp.status == 200
        data = await resp.json()
        assert data["success"] is True
        assert len(data["data"]) >= 1
        assert data["data"][0]["slug"] == "catan"

        resp = await request_context.post("/api/search", data={"query": "catan"})
        assert resp.status == 200
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["slug"] == "catan"

        await request_context.dispose()
        await browser.close()
