import argparse
import asyncio
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.async_api import APIRequestContext, async_playwright

from app.services.palworld_card_service import (
    PalworldCard,
    PalworldPrinting,
    ProvenanceRecord,
    base_card_id,
    validate_snapshot,
)

EN_API_URL = "https://en.palworld-official-cardgame.com/manage/card-list-user/list"
JA_API_URL = "https://palworld-official-cardgame.com/manage/card-list-user/list"
EN_LIST_URL = "https://en.palworld-official-cardgame.com/cardlist/searchresults?expansion=EBP01"
EN_PRODUCT_URL = "https://en.palworld-official-cardgame.com/products/bp01"
JA_PRODUCT_URL = "https://palworld-official-cardgame.com/products/bp01"
COMMUNITY_JSON_URL = "https://raw.githubusercontent.com/Balbi/TCG-Arena-Palworld/main/PalworldCards.json"
COMMUNITY_REPO_URL = "https://github.com/Balbi/TCG-Arena-Palworld"
PRODUCT_SPEC_PRINTING_COUNT = 161
KEYWORDS = {
    "Interrupt",
    "Nocturnal",
    "Taunt",
    "Vigilance",
    "Assault",
    "Stealth",
    "Brave",
    "Retaliate",
    "Breakthrough",
    "Serious",
}
CANONICAL_API_FIELDS = (
    "card_number",
    "card_name",
    "card_kind",
    "card_kind_sub",
    "rare",
    "expansion",
    "expansion_name",
    "color",
    "type",
    "aptitude",
    "cost",
    "power",
    "attack",
    "text",
)


def _api_params(page: int) -> dict[str, str]:
    return {
        "expansion": "EBP01",
        "title": "EBP01",
        "page": str(page),
        "per_page": "100",
        "sort": "new",
    }


async def _fetch_page(request: APIRequestContext, api_url: str, page: int) -> dict[str, Any]:
    response = await request.get(api_url, params=_api_params(page))
    if not response.ok:
        raise ValueError(f"Official Palworld API failed: {api_url} page={page} HTTP {response.status}")
    payload = await response.json()
    if not isinstance(payload, dict) or "items" not in payload or "total" not in payload:
        raise ValueError(f"Official Palworld API contract changed: {api_url} page={page}")
    return payload


async def _fetch_all(request: APIRequestContext, api_url: str) -> tuple[list[dict[str, Any]], int]:
    first = await _fetch_page(request, api_url, 1)
    total = int(first["total"])
    per_page = int(first.get("per_page") or 100)
    rows = list(first["items"])
    page_count = math.ceil(total / per_page) if total else 1
    for page in range(2, page_count + 1):
        payload = await _fetch_page(request, api_url, page)
        if int(payload["total"]) != total:
            raise ValueError(f"Official Palworld API total changed during import: {total} -> {payload['total']}")
        rows.extend(payload["items"])
    if len(rows) != total:
        raise ValueError(f"Official Palworld API pagination mismatch: reported={total}, fetched={len(rows)}")
    return rows, total


def _partition_bp01_rows(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    included: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for row in rows:
        card_number = row.get("card_number")
        if isinstance(card_number, str) and card_number.startswith("EBP01-"):
            included.append(row)
            continue
        excluded.append(
            {
                "api_record_id": row.get("id"),
                "card_number": card_number,
                "card_name": row.get("card_name"),
                "card_kind": row.get("card_kind"),
                "rarity": row.get("rare"),
                "expansion": row.get("expansion"),
            }
        )
    return included, excluded


def _canonical_projection(row: dict[str, Any]) -> dict[str, Any]:
    return {field: row.get(field) for field in CANONICAL_API_FIELDS}


def _deduplicate_official_rows(rows: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        card_number = row.get("card_number")
        if not isinstance(card_number, str) or not card_number.startswith("EBP01-"):
            raise ValueError(f"Unexpected canonical BP01 card number: {card_number!r}")
        grouped[card_number].append(row)

    unique: dict[str, dict[str, Any]] = {}
    duplicates: list[dict[str, Any]] = []
    for card_number, candidates in sorted(grouped.items()):
        projections = [_canonical_projection(candidate) for candidate in candidates]
        if any(projection != projections[0] for projection in projections[1:]):
            raise ValueError(f"Conflicting duplicate official rows for {card_number}")
        unique[card_number] = candidates[0]
        if len(candidates) > 1:
            duplicates.append(
                {
                    "printing_id": card_number,
                    "api_record_ids": [candidate.get("id") for candidate in candidates],
                    "count": len(candidates),
                }
            )
    return unique, duplicates


def _int_or_none(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _pipe_list(value: Any) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in str(value).split("|") if part.strip()]


def _detail_url(base_url: str, row: dict[str, Any]) -> str:
    record_id = row.get("id")
    if record_id is None:
        raise ValueError(f"Official API row has no detail id: {row.get('card_number')}")
    return f"{base_url}/cardlist/detail?id={record_id}"


def _keywords(text: str | None) -> list[str]:
    if not text:
        return []
    folded = text.casefold()
    return sorted(keyword for keyword in KEYWORDS if keyword.casefold() in folded)


def _field_provenance(
    entity_type: str,
    entity_id: str,
    payload: dict[str, Any],
    source_url: str,
    retrieved_at: str,
    source_type: str = "official",
    verification_status: str = "verified_official",
) -> list[dict[str, Any]]:
    ignored = {"source_url", "source_url_en", "source_url_ja", "source_checked_at"}
    return [
        ProvenanceRecord(
            entity_type=entity_type,
            entity_id=entity_id,
            field=field,
            value=value,
            source_url=source_url,
            retrieved_at=retrieved_at,
            source_type=source_type,
            verification_status=verification_status,
        ).model_dump()
        for field, value in payload.items()
        if field not in ignored
    ]


def _build_cards(
    en_rows: dict[str, dict[str, Any]],
    ja_rows: dict[str, dict[str, Any]],
    retrieved_at: str,
) -> tuple[list[PalworldCard], list[dict[str, Any]]]:
    cards: list[PalworldCard] = []
    provenance: list[dict[str, Any]] = []
    logical_ids = sorted({base_card_id(printing_id) for printing_id in en_rows})
    for card_base_id in logical_ids:
        if card_base_id not in en_rows:
            raise ValueError(f"Logical card has no base printing: {card_base_id}")
        row = en_rows[card_base_id]
        ja = ja_rows.get(card_base_id)
        source_url_en = _detail_url("https://en.palworld-official-cardgame.com", row)
        source_url_ja = _detail_url("https://palworld-official-cardgame.com", ja) if ja else None
        card = PalworldCard(
            card_base_id=card_base_id,
            name_ja=ja.get("card_name") if ja else None,
            name_en=str(row["card_name"]),
            card_type=str(row["card_kind"]),
            subtype=row.get("card_kind_sub") or None,
            color=str(row["color"]),
            cost=_int_or_none(row.get("cost")),
            power_or_durability=_int_or_none(row.get("power")),
            strike=_int_or_none(row.get("attack")),
            elements=_pipe_list(row.get("type")),
            aptitudes=_pipe_list(row.get("aptitude")),
            keywords=_keywords(row.get("text")),
            effect_text_ja=ja.get("text") if ja else None,
            effect_text_en=row.get("text") or None,
            product_code="EBP01",
            source_url_ja=source_url_ja,
            source_url_en=source_url_en,
            source_checked_at=retrieved_at,
        )
        cards.append(card)
        provenance.extend(
            _field_provenance(
                "card",
                card_base_id,
                card.model_dump(exclude={"name_ja", "effect_text_ja", "source_url_ja"}),
                source_url_en,
                retrieved_at,
            )
        )
        if ja:
            provenance.extend(
                _field_provenance(
                    "card",
                    card_base_id,
                    {"name_ja": card.name_ja, "effect_text_ja": card.effect_text_ja},
                    source_url_ja or JA_API_URL,
                    retrieved_at,
                )
            )
    return cards, provenance


def _build_printings(
    en_rows: dict[str, dict[str, Any]], retrieved_at: str
) -> tuple[list[PalworldPrinting], list[dict[str, Any]]]:
    printings: list[PalworldPrinting] = []
    provenance: list[dict[str, Any]] = []
    for printing_id, row in sorted(en_rows.items()):
        source_url = _detail_url("https://en.palworld-official-cardgame.com", row)
        printing = PalworldPrinting(
            printing_id=printing_id,
            card_base_id=base_card_id(printing_id),
            rarity=str(row["rare"]),
            is_parallel=printing_id != base_card_id(printing_id),
            official_image_url=None,
            source_url=source_url,
            source_checked_at=retrieved_at,
        )
        printings.append(printing)
        provenance.extend(
            _field_provenance("printing", printing_id, printing.model_dump(), source_url, retrieved_at)
        )
    return printings, provenance


def compare_community_seed(
    community: dict[str, Any],
    cards: list[PalworldCard],
    printings: list[PalworldPrinting],
    retrieved_at: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cards_by_id = {card.card_base_id: card for card in cards}
    printings_by_id = {printing.printing_id: printing for printing in printings}
    mismatches: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    field_map = {
        "name": lambda card, printing: card.name_en,
        "type": lambda card, printing: card.card_type,
        "cost": lambda card, printing: card.cost,
        "Color": lambda card, printing: [card.color],
        "Power": lambda card, printing: "" if card.power_or_durability is None else str(card.power_or_durability),
        "Strike": lambda card, printing: "" if card.strike is None else str(card.strike),
        "Rarity": lambda card, printing: printing.rarity,
    }
    for printing_id, seed in community.items():
        if printing_id not in printings_by_id:
            continue
        printing = printings_by_id[printing_id]
        card = cards_by_id[printing.card_base_id]
        for field, getter in field_map.items():
            if field not in seed:
                continue
            official_value = getter(card, printing)
            community_value = seed[field]
            status = "matched_official" if community_value == official_value else "mismatch_official_wins"
            if status == "mismatch_official_wins":
                mismatches.append(
                    {
                        "printing_id": printing_id,
                        "field": field,
                        "official_value": official_value,
                        "community_value": community_value,
                    }
                )
            provenance.extend(
                _field_provenance(
                    "printing",
                    printing_id,
                    {field: community_value},
                    COMMUNITY_JSON_URL,
                    retrieved_at,
                    source_type="community_seed",
                    verification_status=status,
                )
            )
    return mismatches, provenance


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


async def import_bp01(output_dir: Path, expected_cards: int, expected_printings: int) -> None:
    retrieved_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    async with async_playwright() as playwright:
        request = await playwright.request.new_context()
        en_api_rows, en_reported_total = await _fetch_all(request, EN_API_URL)
        ja_api_rows, ja_reported_total = await _fetch_all(request, JA_API_URL)
        community_response = await request.get(COMMUNITY_JSON_URL)
        if not community_response.ok:
            raise ValueError(f"Community seed fetch failed: HTTP {community_response.status}")
        community = await community_response.json()
        await request.dispose()

    en_bp01_rows, en_excluded_rows = _partition_bp01_rows(en_api_rows)
    ja_bp01_rows, ja_excluded_rows = _partition_bp01_rows(ja_api_rows)
    en_rows, official_duplicates = _deduplicate_official_rows(en_bp01_rows)
    ja_rows, japanese_duplicates = _deduplicate_official_rows(ja_bp01_rows) if ja_bp01_rows else ({}, [])

    cards, card_provenance = _build_cards(en_rows, ja_rows, retrieved_at)
    printings, printing_provenance = _build_printings(en_rows, retrieved_at)
    cards, printings = validate_snapshot(
        cards,
        printings,
        expected_cards=expected_cards,
        expected_printings=expected_printings,
    )

    community_mismatches, community_provenance = compare_community_seed(
        community, cards, printings, retrieved_at
    )
    provenance = card_provenance + printing_provenance + community_provenance
    provenance.sort(key=lambda row: (row["entity_type"], row["entity_id"], row["field"], row["source_type"]))

    japanese_status = "available" if ja_rows else "unavailable_empty_official_api"
    manifest = {
        "schema_version": 1,
        "product_code": "EBP01",
        "logical_card_count": len(cards),
        "printing_count": len(printings),
        "product_spec_printing_count": PRODUCT_SPEC_PRINTING_COUNT,
        "english_api_reported_total": en_reported_total,
        "english_api_bp01_row_count": len(en_bp01_rows),
        "english_api_unique_bp01_printings": len(en_rows),
        "english_api_excluded_non_bp01_count": len(en_excluded_rows),
        "japanese_api_reported_total": ja_reported_total,
        "japanese_source_status": japanese_status,
        "source_checked_at": retrieved_at,
        "official_sources": {
            "english_api": EN_API_URL,
            "english_card_list": EN_LIST_URL,
            "english_product": EN_PRODUCT_URL,
            "japanese_api": JA_API_URL,
            "japanese_product": JA_PRODUCT_URL,
        },
        "community_seed": {"repository": COMMUNITY_REPO_URL, "json": COMMUNITY_JSON_URL},
    }
    audit = {
        "product_code": "EBP01",
        "source_checked_at": retrieved_at,
        "duplicate_card_ids": [],
        "duplicate_printing_ids": [],
        "orphan_printings": [],
        "official_api_duplicate_bp01_record_count": len(en_bp01_rows) - len(en_rows),
        "official_api_duplicate_bp01_records": official_duplicates,
        "official_api_excluded_non_bp01_records": en_excluded_rows,
        "japanese_api_excluded_non_bp01_records": ja_excluded_rows,
        "japanese_api_duplicate_bp01_records": japanese_duplicates,
        "product_spec_vs_unique_api_delta": len(printings) - PRODUCT_SPEC_PRINTING_COUNT,
        "community_mismatch_count": len(community_mismatches),
        "community_mismatches": community_mismatches,
        "policy": "Canonical BP01 printings are official rows whose card_number starts with EBP01-. Official non-BP01 expansion records are audited but excluded. Official fields win over the community seed.",
    }
    _write_json(output_dir / "cards.json", [card.model_dump() for card in cards])
    _write_json(output_dir / "printings.json", [printing.model_dump() for printing in printings])
    _write_json(output_dir / "provenance.json", provenance)
    _write_json(output_dir / "audit.json", audit)
    _write_json(output_dir / "manifest.json", manifest)


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Palworld OCG BP01 from the official API")
    parser.add_argument("--output", type=Path, default=Path("data/palworld/bp01"))
    parser.add_argument("--expected-cards", type=int, default=100)
    parser.add_argument("--expected-printings", type=int, default=161)
    args = parser.parse_args()
    asyncio.run(import_bp01(args.output, args.expected_cards, args.expected_printings))


if __name__ == "__main__":
    main()
