import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data" / "palworld" / "bp01"
CARD_ID_PATTERN = re.compile(r"^([A-Z0-9]+-\d{3})")


class PalworldCard(BaseModel):
    card_base_id: str
    name_ja: str | None = None
    name_en: str
    card_type: str
    subtype: str | None = None
    color: str
    cost: int | None = None
    power_or_durability: int | None = None
    strike: int | None = None
    elements: list[str] = []
    aptitudes: list[str] = []
    keywords: list[str] = []
    effect_text_ja: str | None = None
    effect_text_en: str | None = None
    product_code: str
    source_url_ja: str | None = None
    source_url_en: str
    source_checked_at: str


class PalworldPrinting(BaseModel):
    printing_id: str
    card_base_id: str
    rarity: str
    is_parallel: bool
    official_image_url: str | None = None
    source_url: str
    source_checked_at: str


class ProvenanceRecord(BaseModel):
    entity_type: str
    entity_id: str
    field: str
    value: Any
    source_url: str
    retrieved_at: str
    source_type: str
    verification_status: str


def base_card_id(printing_id: str) -> str:
    match = CARD_ID_PATTERN.match(printing_id)
    if not match:
        raise ValueError(f"Invalid Palworld card number: {printing_id}")
    return match.group(1)


def validate_snapshot(
    cards: list[dict[str, Any]] | list[PalworldCard],
    printings: list[dict[str, Any]] | list[PalworldPrinting],
    expected_cards: int | None = None,
    expected_printings: int | None = None,
) -> tuple[list[PalworldCard], list[PalworldPrinting]]:
    parsed_cards = [card if isinstance(card, PalworldCard) else PalworldCard.model_validate(card) for card in cards]
    parsed_printings = [
        printing if isinstance(printing, PalworldPrinting) else PalworldPrinting.model_validate(printing)
        for printing in printings
    ]

    card_ids = [card.card_base_id for card in parsed_cards]
    printing_ids = [printing.printing_id for printing in parsed_printings]
    duplicate_cards = sorted({card_id for card_id in card_ids if card_ids.count(card_id) > 1})
    duplicate_printings = sorted({printing_id for printing_id in printing_ids if printing_ids.count(printing_id) > 1})
    if duplicate_cards:
        raise ValueError(f"Duplicate logical card IDs: {duplicate_cards}")
    if duplicate_printings:
        raise ValueError(f"Duplicate printing IDs: {duplicate_printings}")

    known_cards = set(card_ids)
    orphan_printings = sorted(
        printing.printing_id for printing in parsed_printings if printing.card_base_id not in known_cards
    )
    if orphan_printings:
        raise ValueError(f"Orphan printings: {orphan_printings}")

    malformed_links = sorted(
        printing.printing_id
        for printing in parsed_printings
        if base_card_id(printing.printing_id) != printing.card_base_id
    )
    if malformed_links:
        raise ValueError(f"Printing/base-card mapping mismatch: {malformed_links}")

    if expected_cards is not None and len(parsed_cards) != expected_cards:
        raise ValueError(f"Expected {expected_cards} logical cards, got {len(parsed_cards)}")
    if expected_printings is not None and len(parsed_printings) != expected_printings:
        raise ValueError(f"Expected {expected_printings} printings, got {len(parsed_printings)}")

    return parsed_cards, parsed_printings


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_snapshot(data_dir: Path = DEFAULT_DATA_DIR) -> dict[str, Any]:
    manifest = _read_json(data_dir / "manifest.json")
    raw_cards = _read_json(data_dir / "cards.json")
    raw_printings = _read_json(data_dir / "printings.json")
    cards, printings = validate_snapshot(
        raw_cards,
        raw_printings,
        expected_cards=manifest["logical_card_count"],
        expected_printings=manifest["printing_count"],
    )
    return {
        "manifest": manifest,
        "cards": cards,
        "printings": printings,
        "provenance": _read_json(data_dir / "provenance.json"),
        "audit": _read_json(data_dir / "audit.json"),
    }


def search_cards(
    query: str | None = None,
    color: str | None = None,
    card_type: str | None = None,
    rarity: str | None = None,
    limit: int = 100,
    offset: int = 0,
    data_dir: Path = DEFAULT_DATA_DIR,
) -> dict[str, Any]:
    snapshot = load_snapshot(data_dir)
    printings_by_card: dict[str, list[PalworldPrinting]] = defaultdict(list)
    for printing in snapshot["printings"]:
        printings_by_card[printing.card_base_id].append(printing)

    normalized_query = query.casefold().strip() if query else None
    normalized_color = color.casefold().strip() if color else None
    normalized_type = card_type.casefold().strip() if card_type else None
    normalized_rarity = rarity.casefold().strip() if rarity else None
    matches: list[dict[str, Any]] = []

    for card in snapshot["cards"]:
        card_printings = sorted(printings_by_card[card.card_base_id], key=lambda item: item.printing_id)
        rarity_printings = [
            printing for printing in card_printings if printing.rarity.casefold() == normalized_rarity
        ] if normalized_rarity else card_printings
        if normalized_rarity and not rarity_printings:
            continue
        if normalized_color and card.color.casefold() != normalized_color:
            continue
        if normalized_type and card.card_type.casefold() != normalized_type:
            continue
        if normalized_query:
            searchable = [card.card_base_id, card.name_en, card.name_ja or ""]
            searchable.extend(printing.printing_id for printing in card_printings)
            if not any(normalized_query in value.casefold() for value in searchable):
                continue
        matches.append(
            {
                "card": card.model_dump(),
                "printings": [printing.model_dump() for printing in rarity_printings],
            }
        )

    total = len(matches)
    return {
        "data": matches[offset : offset + limit],
        "pagination": {"total": total, "limit": limit, "offset": offset, "count": len(matches[offset : offset + limit])},
        "manifest": snapshot["manifest"],
    }


def get_card(card_base_id: str, data_dir: Path = DEFAULT_DATA_DIR) -> dict[str, Any] | None:
    snapshot = load_snapshot(data_dir)
    card = next((item for item in snapshot["cards"] if item.card_base_id == card_base_id), None)
    if card is None:
        return None
    printings = sorted(
        (printing for printing in snapshot["printings"] if printing.card_base_id == card_base_id),
        key=lambda item: item.printing_id,
    )
    return {"card": card.model_dump(), "printings": [printing.model_dump() for printing in printings]}
