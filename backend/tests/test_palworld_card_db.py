import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.services.palworld_card_service import base_card_id, search_cards, validate_snapshot


def card(card_base_id: str, name_en: str, color: str = "Red", card_type: str = "Pal") -> dict:
    return {
        "card_base_id": card_base_id,
        "name_ja": "テスト",
        "name_en": name_en,
        "card_type": card_type,
        "subtype": "Lucky Pal" if card_type == "Pal" else None,
        "color": color,
        "cost": 7,
        "power_or_durability": 1200,
        "strike": 3,
        "elements": ["Fire"],
        "aptitudes": ["Kindling"],
        "keywords": [],
        "effect_text_ja": "効果",
        "effect_text_en": "Effect",
        "product_code": "EBP01",
        "source_url_ja": "https://palworld-official-cardgame.com/cardlist/detail?id=1",
        "source_url_en": "https://en.palworld-official-cardgame.com/cardlist/detail?id=1",
        "source_checked_at": "2026-08-11T00:00:00+00:00",
    }


def printing(printing_id: str, rarity: str) -> dict:
    return {
        "printing_id": printing_id,
        "card_base_id": base_card_id(printing_id),
        "rarity": rarity,
        "is_parallel": printing_id != base_card_id(printing_id),
        "official_image_url": "https://example.invalid/card.webp",
        "source_url": "https://en.palworld-official-cardgame.com/cardlist/detail?id=1",
        "source_checked_at": "2026-08-11T00:00:00+00:00",
    }


def write_snapshot(path: Path) -> None:
    cards = [
        card("EBP01-002", "Suzaku – Hellfire Wings"),
        card("EBP01-039", "Antique Curtain", color="Blue", card_type="Structure"),
    ]
    printings = [
        printing("EBP01-002", "RR"),
        printing("EBP01-002OSR", "OSR"),
        printing("EBP01-002SP", "SP"),
        printing("EBP01-039", "U"),
        printing("EBP01-039SR", "SR"),
    ]
    path.mkdir(parents=True)
    (path / "cards.json").write_text(json.dumps(cards), encoding="utf-8")
    (path / "printings.json").write_text(json.dumps(printings), encoding="utf-8")
    (path / "provenance.json").write_text("[]", encoding="utf-8")
    (path / "audit.json").write_text(
        json.dumps({"community_mismatch_count": 0, "policy": "official wins"}), encoding="utf-8"
    )
    (path / "manifest.json").write_text(
        json.dumps({"logical_card_count": 2, "printing_count": 5}), encoding="utf-8"
    )


def test_parallel_printings_share_logical_card() -> None:
    assert base_card_id("EBP01-002") == "EBP01-002"
    assert base_card_id("EBP01-002OSR") == "EBP01-002"
    assert base_card_id("EBP01-002SP") == "EBP01-002"


def test_schema_validation_rejects_missing_required_field() -> None:
    malformed = card("EBP01-002", "Suzaku – Hellfire Wings")
    malformed.pop("color")
    with pytest.raises(ValidationError):
        validate_snapshot([malformed], [printing("EBP01-002", "RR")])


def test_duplicate_printing_is_rejected() -> None:
    duplicate = printing("EBP01-002", "RR")
    with pytest.raises(ValueError, match="Duplicate printing IDs"):
        validate_snapshot([card("EBP01-002", "Suzaku – Hellfire Wings")], [duplicate, duplicate])


def test_orphan_printing_is_rejected() -> None:
    with pytest.raises(ValueError, match="Orphan printings"):
        validate_snapshot(
            [card("EBP01-002", "Suzaku – Hellfire Wings")],
            [printing("EBP01-039", "U")],
        )


def test_expected_counts_fail_closed() -> None:
    with pytest.raises(ValueError, match="Expected 100 logical cards"):
        validate_snapshot(
            [card("EBP01-002", "Suzaku – Hellfire Wings")],
            [printing("EBP01-002", "RR")],
            expected_cards=100,
            expected_printings=161,
        )


def test_search_supports_number_name_color_type_and_rarity(tmp_path: Path) -> None:
    write_snapshot(tmp_path)
    by_number = search_cards(query="EBP01-002SP", data_dir=tmp_path)
    by_name = search_cards(query="Suzaku", data_dir=tmp_path)
    by_color_type = search_cards(color="Blue", card_type="Structure", data_dir=tmp_path)
    by_rarity = search_cards(rarity="OSR", data_dir=tmp_path)

    assert by_number["pagination"]["total"] == 1
    assert by_name["data"][0]["card"]["card_base_id"] == "EBP01-002"
    assert by_color_type["data"][0]["card"]["card_base_id"] == "EBP01-039"
    assert [item["printing_id"] for item in by_rarity["data"][0]["printings"]] == ["EBP01-002OSR"]
