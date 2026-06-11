import io
import logging
import os
import tempfile
from datetime import datetime, timezone

from fastapi import APIRouter, Query, HTTPException, Response
from pdf2image import convert_from_path
from playwright.async_api import async_playwright

from app.core import sqlite_client
from app.models import SearchRequest, SyncPushRequest, UserReviewUpdate, UserCollectionUpdate
from app.services.game_master_service import GameMasterService
from app.services.ranking_service import get_top_rated_games
from app.services.youtube_scraper import scrape_youtube_videos
from app.utils import slugify

logger = logging.getLogger("routers.games")
router = APIRouter()
game_master = GameMasterService()


@router.get("/games")
async def list_games(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
    games = sqlite_client.list_games(limit=limit, offset=offset)
    total = sqlite_client.get_total_games()
    return {
        "success": True,
        "data": games,
        "pagination": {"total": total, "limit": limit, "offset": offset, "count": len(games)},
    }


@router.get("/games/top-rated")
async def top_rated_games_endpoint(limit: int = Query(20, ge=1, le=50)):
    games = get_top_rated_games(limit=limit)
    return {"success": True, "data": games}


@router.get("/games/search")
async def search_games_endpoint(
    query: str | None = Query(None, alias="q"),
    min_players: int | None = Query(None),
    max_players: int | None = Query(None),
    play_time: int | None = Query(None),
    mechanics: str | None = Query(None, description="Comma-separated list of mechanics"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    mech_list = [m.strip() for m in mechanics.split(",")] if mechanics else None
    games = sqlite_client.search_games(
        query=query,
        min_players=min_players,
        max_players=max_players,
        play_time=play_time,
        mechanics=mech_list,
        limit=limit,
        offset=offset,
    )
    return {"success": True, "data": games}


@router.get("/games/autocomplete")
async def autocomplete_endpoint(query: str = Query(..., alias="q"), limit: int = Query(10, ge=1, le=50)):
    suggestions = sqlite_client.autocomplete_suggestions(query, limit=limit)
    return {"success": True, "data": suggestions}


@router.get("/games/skeletons")
async def list_game_skeletons():
    skeletons = sqlite_client.get_game_skeletons()
    return {"success": True, "data": skeletons}


@router.get("/games/{slug}")
async def get_game(slug: str):
    game = sqlite_client.get_game_by_slug(slug)
    return {"success": True, "data": game}


@router.get("/games/{slug}/credits")
async def get_game_credits(slug: str):
    credits = sqlite_client.get_game_credits(slug)
    return {"success": True, "data": credits}


@router.get("/games/{slug}/expansions")
async def get_game_expansions(slug: str):
    expansions = sqlite_client.get_game_expansions(slug)
    return {"success": True, "data": expansions}


@router.post("/games/sync")
async def sync_game(
    bgg_id: int | None = Query(None, description="BGG ID to sync from BoardGameGeek"),
    game_name: str | None = Query(None, description="The official name of the board game to reconstruct")
):
    """
    Sync game from BoardGameGeek by bgg_id, or reconstruct/generate a high-resolution guide by game_name.
    """
    if bgg_id is not None:
        logger.info(f"Syncing game with BGG ID: {bgg_id}")
        from app.services.bgg_service import BGGService
        bgg_service = BGGService()
        game = await bgg_service.fetch_and_upsert_game(bgg_id)
        if not game:
            return {"success": False, "message": f"Failed to sync game with BGG ID {bgg_id}"}
        return {"success": True, "data": game, "message": "Game synced from BGG successfully"}
    elif game_name is not None:
        logger.info(f"Reconstructing guide for: {game_name}")
        game = await game_master.generate_and_save_game_guide(game_name)
        return {"success": True, "data": game, "message": "High-Res Guide generated successfully"}
    else:
        return {"success": False, "message": "Either bgg_id or game_name must be provided"}


@router.delete("/games/{slug}")
async def delete_game_endpoint(slug: str):
    sqlite_client.delete_game(slug)
    return {"success": True, "message": f"Game '{slug}' deleted"}


@router.post("/search")
async def post_search(body: SearchRequest):
    results = sqlite_client.search_games(query=body.query)
    if results:
        return {"success": True, "data": results[0]}

    if body.generate:
        game = await game_master.generate_and_save_game_guide(body.query)
        return {"success": True, "data": game}

    return {"success": False, "message": "Game not found in database. Set generate=true to trigger generation."}


@router.get("/sync/pull")
async def sync_pull(last_sync_at: str | None = Query(None, description="ISO-8601 timestamp of last sync")):
    now = datetime.now(timezone.utc).isoformat()
    changed_games = sqlite_client.get_games_modified_since(last_sync_at)
    return {"success": True, "last_sync_at": now, "changed": changed_games, "deleted": []}


@router.post("/sync/push")
async def sync_push(payload: SyncPushRequest):
    now = datetime.now(timezone.utc).isoformat()
    updated_games = []
    for game in payload.games:
        game_dict = game.model_dump()
        # Ensure slug is present
        if not game_dict.get("slug") and game_dict.get("title"):
            game_dict["slug"] = slugify(game_dict["title"])
        upserted = sqlite_client.upsert_game(game_dict)
        updated_games.append(upserted)
    return {"success": True, "last_sync_at": now, "updated": updated_games}


@router.get("/games/{slug}/review")
async def get_user_review(slug: str, user_id: str = Query(..., description="User ID of the reviewer")):
    review = sqlite_client.get_user_review(slug, user_id)
    return {"success": True, "data": review}


@router.post("/games/{slug}/review")
async def create_or_update_user_review(slug: str, review_data: UserReviewUpdate):
    # Mock authentication - check if user_id is provided
    if not review_data.user_id:
        raise HTTPException(status_code=403, detail="User ID is required")
        
    review = sqlite_client.upsert_user_review(
        slug, 
        review_data.user_id, 
        review_data.rating, 
        review_data.comment, 
        review_data.verified_purchase
    )
    return {"success": True, "data": review}


@router.delete("/games/{slug}/review")
async def delete_user_review(slug: str, user_id: str = Query(..., description="User ID of the reviewer")):
    sqlite_client.delete_user_review(slug, user_id)
    return {"success": True, "message": "Review deleted"}


@router.get("/games/{slug}/shelf")
async def get_user_collection(slug: str):
    collection = sqlite_client.get_user_collection(slug)
    return {"success": True, "data": collection}


@router.post("/games/{slug}/shelf")
async def create_or_update_user_collection(slug: str, collection_data: UserCollectionUpdate):
    collection = sqlite_client.upsert_user_collection(slug, collection_data.status)
    return {"success": True, "data": collection}


@router.delete("/games/{slug}/shelf")
async def delete_user_collection(slug: str):
    sqlite_client.delete_user_collection(slug)
    return {"success": True, "message": "Removed from shelf"}


@router.get("/games/{slug}/videos")
async def get_game_videos(slug: str):
    videos = sqlite_client.get_videos(slug)
    if not videos:
        game = sqlite_client.get_game_by_slug(slug)
        title = game["title"]
        scraped = await scrape_youtube_videos(title, limit=5)
        sqlite_client.save_videos(slug, scraped)
        videos = sqlite_client.get_videos(slug)
    return {"success": True, "data": videos}


@router.get("/games/{slug}/artworks")
async def get_game_artworks(slug: str):
    artworks = sqlite_client.get_artworks(slug)
    return {"success": True, "data": artworks}


@router.post("/games/{slug}/artworks")
async def add_game_artworks(slug: str, artworks: list[dict]):
    sqlite_client.save_artworks(slug, artworks)
    return {"success": True, "message": "Artworks updated"}


@router.get("/pdf/proxy")
async def pdf_image_proxy(
    url: str = Query(..., description="URL of the PDF file"),
    page: int = Query(1, ge=1, description="Page number to render (1-indexed)"),
):
    async with async_playwright() as p:
        request_context = await p.request.new_context()
        resp = await request_context.get(url)
        if resp.status != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch PDF from URL")
        pdf_bytes = await resp.body()

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name

    try:
        images = convert_from_path(tmp_path, dpi=150, first_page=page, last_page=page)
        if not images:
            raise HTTPException(status_code=404, detail="Page not found in PDF")

        img_byte_arr = io.BytesIO()
        images[0].save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)
        return Response(content=img_byte_arr.getvalue(), media_type="image/png")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
