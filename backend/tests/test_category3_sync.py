import pytest
from app.core import sqlite_client
from app.main import CacheControlledStaticFiles
from app.models import GameDetail, SyncPushRequest
from app.routers import list_game_skeletons, sync_pull, sync_push
from starlette.responses import Response


@pytest.mark.asyncio
async def test_sync_skeletons():
    # Insert a dummy game first
    dummy_game = {
        "slug": "test-game-slug",
        "title": "Test Game Title",
        "title_ja": "テストゲーム",
        "image_url": "http://example.com/image.png",
        "min_players": 2,
        "max_players": 4,
        "play_time": 60,
    }
    sqlite_client.upsert_game(dummy_game)

    # 1. Call list_game_skeletons directly
    res = await list_game_skeletons()
    assert res["success"] is True
    assert len(res["data"]) >= 1

    # Check skeleton fields
    skeleton = next(item for item in res["data"] if item["slug"] == "test-game-slug")
    assert skeleton["title"] == "Test Game Title"
    assert skeleton["title_ja"] == "テストゲーム"
    assert skeleton["image_url"] == "http://example.com/image.png"
    assert skeleton["min_players"] == 2  # noqa: PLR2004
    assert skeleton["max_players"] == 4  # noqa: PLR2004
    assert skeleton["play_time"] == 60  # noqa: PLR2004


@pytest.mark.asyncio
async def test_sync_pull_and_push():
    pushed_game = GameDetail(
        id="123",
        slug="pushed-game-slug",
        title="Pushed Game",
        title_ja="プッシュゲーム",
        description="A pushed game description",
        min_players=1,
        max_players=5,
        play_time=30,
    )

    payload = SyncPushRequest(games=[pushed_game])

    # Test sync push
    res = await sync_push(payload)
    assert res["success"] is True
    assert len(res["updated"]) == 1
    assert res["updated"][0]["slug"] == "pushed-game-slug"

    # Test sync pull
    pull_res = await sync_pull(last_sync_at="2000-01-01T00:00:00")
    assert pull_res["success"] is True
    assert any(g["slug"] == "pushed-game-slug" for g in pull_res["changed"])

    # Clean up test games
    sqlite_client.delete_game("test-game-slug")
    sqlite_client.delete_game("pushed-game-slug")


def test_static_files_cache_control(tmp_path):
    # Test CacheControlledStaticFiles directly
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    test_file = static_dir / "test.txt"
    test_file.write_text("hello world")

    static_files = CacheControlledStaticFiles(directory=str(static_dir))

    # We can mock/call file_response directly
    response = static_files.file_response("test.txt", stat_result=test_file.stat(), scope={"headers": []})
    assert isinstance(response, Response)
    assert response.headers.get("cache-control") == "public, max-age=31536000, immutable"
