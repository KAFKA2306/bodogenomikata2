from fastapi import APIRouter, HTTPException, Query

from app.services.palworld_card_service import DEFAULT_DATA_DIR, get_card, load_snapshot, search_cards

router = APIRouter()


@router.get("/palworld/cards")
async def list_palworld_cards(
    query: str | None = Query(None, alias="q"),
    color: str | None = Query(None),
    card_type: str | None = Query(None),
    rarity: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return {
        "success": True,
        **search_cards(
            query=query,
            color=color,
            card_type=card_type,
            rarity=rarity,
            limit=limit,
            offset=offset,
        ),
    }


@router.get("/palworld/cards/{card_base_id}")
async def get_palworld_card(card_base_id: str):
    result = get_card(card_base_id.upper())
    if result is None:
        raise HTTPException(status_code=404, detail="Palworld card not found")
    return {"success": True, "data": result}


@router.get("/palworld/meta")
async def palworld_card_meta():
    snapshot = load_snapshot(DEFAULT_DATA_DIR)
    return {
        "success": True,
        "manifest": snapshot["manifest"],
        "audit": {
            "community_mismatch_count": snapshot["audit"]["community_mismatch_count"],
            "policy": snapshot["audit"]["policy"],
        },
    }
