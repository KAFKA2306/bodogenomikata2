import os
import re
import unicodedata
from typing import Any
from urllib.parse import parse_qs, quote, urlencode, urlparse, urlunparse


def amazon_search_url(title: str) -> str | None:
    tracking_id = os.getenv("AMAZON_TRACKING_ID")
    if not tracking_id or not tracking_id.strip():
        return None
    q = quote(title)
    return f"https://www.amazon.co.jp/s?k={q}&tag={tracking_id.strip()}"


_AMAZON_DOMAINS = ("amazon.co.jp", "amazon.com")


def ensure_amazon_tag(url: str) -> str:
    tracking_id = os.getenv("AMAZON_TRACKING_ID")
    if not tracking_id or tracking_id.strip() == "":
        return url
    parsed = urlparse(url)
    if not any(d in parsed.netloc for d in _AMAZON_DOMAINS):
        return url
    qs = parse_qs(parsed.query)
    qs["tag"] = tracking_id.strip()
    return urlunparse(parsed._replace(query=urlencode(qs, doseq=True)))


def slugify(title: str) -> str:
    text = unicodedata.normalize("NFKC", title)
    text = text.lower()
    text = re.sub("[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text or "game"


def map_bgg_to_games_schema(bgg_data: dict[str, Any]) -> dict[str, Any]:
    game_id = bgg_data.get("id")
    title = bgg_data.get("name") or "Unknown"
    bgg_url = f"https://boardgamegeek.com/boardgame/{game_id}"
    return {
        "bgg_id": _parse_int(game_id),
        "bgg_url": bgg_url,
        "source_url": bgg_url,
        "slug": slugify(title),
        "title": title,
        "description": bgg_data.get("description"),
        "published_year": _parse_int(bgg_data.get("yearpublished")),
        "min_players": _parse_int(bgg_data.get("minplayers")),
        "max_players": _parse_int(bgg_data.get("maxplayers")),
        "play_time": _parse_int(bgg_data.get("playingtime")),
        "min_age": _parse_int(bgg_data.get("minage")),
        "image_url": bgg_data.get("image"),
    }


def _parse_int(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except (ValueError, TypeError):
        return None
