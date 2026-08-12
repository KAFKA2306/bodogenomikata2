from __future__ import annotations

import json
from pathlib import Path

from app.services.palworld_card_service import base_card_id, search_cards

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "palworld" / "bp01"
OBSOLETE_WORKFLOW = PROJECT_ROOT / ".github" / "workflows" / "weekly-repo-research.yml"


def read_json(name: str):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def require_unique(values: list[str], label: str) -> None:
    duplicates = sorted({value for value in values if values.count(value) > 1})
    if duplicates:
        raise SystemExit(f"duplicate {label}: {duplicates}")


def main() -> None:
    cards = read_json("cards.json")
    printings = read_json("printings.json")
    provenance = read_json("provenance.json")
    manifest = read_json("manifest.json")

    card_ids = [card["card_base_id"] for card in cards]
    printing_ids = [printing["printing_id"] for printing in printings]
    require_unique(card_ids, "card_base_id")
    require_unique(printing_ids, "printing_id")

    known_cards = set(card_ids)
    known_printings = set(printing_ids)
    orphan_printings = sorted(
        printing["printing_id"]
        for printing in printings
        if printing["card_base_id"] not in known_cards
        or base_card_id(printing["printing_id"]) != printing["card_base_id"]
    )
    if orphan_printings:
        raise SystemExit(f"orphan/mismatched printings: {orphan_printings}")

    provenance_keys: list[tuple[str, str, str]] = []
    covered_cards: set[str] = set()
    covered_printings: set[str] = set()
    orphan_provenance: list[str] = []
    for raw in provenance:
        entity_type = raw.get("entity_type")
        entity_id = raw.get("entity_id")
        field = raw.get("field")
        source_url = raw.get("source_url")
        retrieved_at = raw.get("retrieved_at")
        source_type = raw.get("source_type")
        verification_status = raw.get("verification_status")
        if not all(isinstance(value, str) and value for value in (
            entity_type,
            entity_id,
            field,
            source_url,
            retrieved_at,
            source_type,
            verification_status,
        )):
            raise SystemExit(f"incomplete provenance record: {raw}")
        if not source_url.startswith("https://"):
            raise SystemExit(f"non-HTTPS provenance URL: {source_url}")
        provenance_keys.append((entity_type, entity_id, field))
        if entity_type == "card":
            if entity_id not in known_cards:
                orphan_provenance.append(f"card:{entity_id}:{field}")
            covered_cards.add(entity_id)
        elif entity_type == "printing":
            if entity_id not in known_printings:
                orphan_provenance.append(f"printing:{entity_id}:{field}")
            covered_printings.add(entity_id)
        else:
            raise SystemExit(f"unsupported provenance entity_type: {entity_type}")

    require_unique(["\0".join(key) for key in provenance_keys], "provenance entity/field key")
    if orphan_provenance:
        raise SystemExit(f"orphan provenance records: {sorted(orphan_provenance)}")

    missing_card_provenance = sorted(known_cards - covered_cards)
    missing_printing_provenance = sorted(known_printings - covered_printings)
    if missing_card_provenance or missing_printing_provenance:
        raise SystemExit(
            "missing provenance coverage: "
            f"cards={missing_card_provenance}, printings={missing_printing_provenance}"
        )

    if len(cards) != manifest["logical_card_count"]:
        raise SystemExit("manifest logical_card_count mismatch")
    if len(printings) != manifest["printing_count"]:
        raise SystemExit("manifest printing_count mismatch")

    probe = card_ids[0]
    search_result = search_cards(query=probe, data_dir=DATA_DIR)
    if search_result["pagination"]["total"] != 1:
        raise SystemExit(f"canonical search probe failed for {probe}")
    returned = search_result["data"][0]["card"]["card_base_id"]
    if returned != probe:
        raise SystemExit(f"canonical search returned {returned}, expected {probe}")

    if OBSOLETE_WORKFLOW.exists():
        raise SystemExit("obsolete weekly repository research workflow must remain removed")

    print(
        "ratchet ok: "
        f"cards={len(cards)} printings={len(printings)} provenance={len(provenance)} search={probe}"
    )


if __name__ == "__main__":
    main()
