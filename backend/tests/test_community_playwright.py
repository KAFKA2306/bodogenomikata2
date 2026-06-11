import pytest
import subprocess
import time
import socket
import os
from playwright.async_api import async_playwright


def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


@pytest.fixture(scope="module")
def fastapi_server():
    port = 8002
    env = os.environ.copy()
    env["PYTHONPATH"] = "backend"
    env["DATABASE_URL"] = "backend/test_games_community.db"

    test_db = "backend/test_games_community.db"
    if os.path.exists(test_db):
        os.remove(test_db)

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
async def test_community_endpoints(fastapi_server):
    async with async_playwright() as p:
        request_context = await p.request.new_context(base_url=fastapi_server)

        # 1. Get initial review (should be None/null)
        resp = await request_context.get("/api/games/catan/review?user_id=test_user")
        assert resp.status == 200
        data = await resp.json()
        assert data["success"] is True
        assert data["data"] is None

        # 2. Post review
        post_resp = await request_context.post(
            "/api/games/catan/review", data={"user_id": "test_user", "rating": 8.5, "comment": "とても面白いゲームだもんっ！"}
        )
        assert post_resp.status == 200
        post_data = await post_resp.json()
        assert post_data["success"] is True
        assert post_data["data"]["game_slug"] == "catan"
        assert post_data["data"]["rating"] == 8.5
        assert post_data["data"]["comment"] == "とても面白いゲームだもんっ！"

        # 3. Get updated review
        get_resp = await request_context.get("/api/games/catan/review?user_id=test_user")
        assert get_resp.status == 200
        get_data = await get_resp.json()
        assert get_data["success"] is True
        assert get_data["data"]["rating"] == 8.5

        # 4. Get initial shelf status (should be None/null)
        shelf_resp = await request_context.get("/api/games/catan/shelf")
        assert shelf_resp.status == 200
        shelf_data = await shelf_resp.json()
        assert shelf_data["success"] is True
        assert shelf_data["data"] is None

        # 5. Post shelf status
        shelf_post_resp = await request_context.post("/api/games/catan/shelf", data={"status": "owned"})
        assert shelf_post_resp.status == 200
        shelf_post_data = await shelf_post_resp.json()
        assert shelf_post_data["success"] is True
        assert shelf_post_data["data"]["status"] == "owned"

        # 6. Delete review
        del_rev_resp = await request_context.delete("/api/games/catan/review?user_id=test_user")
        assert del_rev_resp.status == 200
        del_rev_data = await del_rev_resp.json()
        assert del_rev_data["success"] is True

        # 7. Get review again (should be None)
        get_rev_again = await request_context.get("/api/games/catan/review?user_id=test_user")
        assert get_rev_again.status == 200
        get_rev_again_data = await get_rev_again.json()
        assert get_rev_again_data["data"] is None

        # 8. Delete shelf status
        del_shelf_resp = await request_context.delete("/api/games/catan/shelf")
        assert del_shelf_resp.status == 200
        del_shelf_data = await del_shelf_resp.json()
        assert del_shelf_data["success"] is True

        # 9. Get shelf status again (should be None)
        get_shelf_again = await request_context.get("/api/games/catan/shelf")
        assert get_shelf_again.status == 200
        get_shelf_again_data = await get_shelf_again.json()
        assert get_shelf_again_data["data"] is None

        await request_context.dispose()
