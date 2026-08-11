import argparse
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.async_api import Page, async_playwright

from app.services.palworld_card_service import (
    PalworldCard,
    PalworldPrinting,
    ProvenanceRecord,
    base_card_id,
    validate_snapshot,
)

EN_LIST_URL = "https://en.palworld-official-cardgame.com/cardlist/searchresults?expansion=EBP01"
JA_LIST_URL = "https://palworld-official-cardgame.com/cardlist/searchresults?expansion=EBP01"
EN_PRODUCT_URL = "https://en.palworld-official-cardgame.com/products/bp01"
JA_PRODUCT_URL = "https://palworld-official-cardgame.com/products/bp01"
COMMUNITY_JSON_URL = "https://raw.githubusercontent.com/Balbi/TCG-Arena-Palworld/main/PalworldCards.json"
COMMUNITY_REPO_URL = "https://github.com/Balbi/TCG-Arena-Palworld"

RARITIES = {"C", "U", "R", "RR", "SR", "OSR", "SP", "SSP", "TD", "TSR", "TSP", "PR"}
CARD_TYPES = {"Pal", "Structure", "Event", "Gear"}
COLORS = {"Red", "Blue", "Green", "Purple", "Colorless"}
ELEMENTS = {"Neutral", "Fire", "Water", "Electric", "Ground", "Grass", "Ice", "Dragon", "Dark"}
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
PRINTING_PATTERN = re.compile(r"\b(EBP01-\d{3}(?:SSP|OSR|SP|SR)?)\b")
APTITUDE_PATTERN = re.compile(r"≪([^≫]+)≫")
NUMBER_PATTERN = re.compile(r"(\d+)")


def _lines(text: str) -> list[str]:
    return [line.strip() for line in text.replace("\r", "").split("\n") if line.strip()]


def _printing_id(text: str) -> str:
    match = PRINTING_PATTERN.search(text)
    if not match:
        raise ValueError(f"Card block has no EBP01 printing ID: {text[:120]}")
    return match.group(1)


def _rarity(lines: list[str], printing_id: str) -> str:
    first = next(line for line in lines if printing_id in line)
    for rarity in sorted(RARITIES, key=len, reverse=True):
        if re.search(rf"\b{rarity}\b", first.replace(printing_id, "")):
            return rarity
    for line in lines:
        if line in RARITIES:
            return line
    raise ValueError(f"Rarity is missing for {printing_id}")


def _name(lines: list[str], printing_id: str, rarity: str) -> str:
    index = next(index for index, line in enumerate(lines) if printing_id in line)
    for line in lines[index + 1 :]:
        if line == rarity or line in RARITIES or line.upper() == "MORE":
            continue
        if line in CARD_TYPES or line in COLORS:
            continue
        if line.startswith(("Cost ", "Power ", "Durability ", "Strike ", "コスト ", "戦闘力", "耐久力", "打撃力")):
            continue
        if "≪" in line:
            continue
        return line
    raise ValueError(f"Name is missing for {printing_id}")


def _number_after_prefix(lines: list[str], prefixes: tuple[str, ...]) -> int | None:
    for line in lines:
        if line.startswith(prefixes):
            match = NUMBER_PATTERN.search(line)
            if match:
                return int(match.group(1))
    return None


def _effect_text(lines: list[str], name: str) -> str | None:
    start = lines.index(name) + 1
    metadata_indexes = [start]
    for index, line in enumerate(lines[start:], start=start):
        if (
            line in RARITIES
            or line in CARD_TYPES
            or line in COLORS
            or "≪" in line
            or line.startswith(("Cost ", "Power ", "Durability ", "Strike ", "コスト ", "戦闘力", "耐久力", "打撃力"))
        ):
            metadata_indexes.append(index)
    last_metadata = max(metadata_indexes)
    effect_lines = [line for line in lines[last_metadata + 1 :] if line.upper() != "MORE"]
    return "\n".join(effect_lines) or None


def _preferred_card_image(images: list[dict[str, Any]], name: str) -> str | None:
    named = [image for image in images if image.get("alt", "").strip() == name and image.get("src")]
    if named:
        return max(named, key=lambda image: image.get("area", 0))["src"]
    candidates = [image for image in images if image.get("src")]
    if not candidates:
        return None
    return max(candidates, key=lambda image: image.get("area", 0))["src"]


def parse_english_block(block: dict[str, Any]) -> dict[str, Any]:
    lines = _lines(block["text"])
    printing_id = _printing_id(block["text"])
    rarity = _rarity(lines, printing_id)
    name = _name(lines, printing_id, rarity)
    card_type = next((line for line in lines if line in CARD_TYPES), None)
    color = next((line for line in lines if line in COLORS), None)
    if card_type is None or color is None:
        raise ValueError(f"Type/color missing for {printing_id}")
    subtype = next((line for line in lines if line in {"Lucky Pal", "Normal Pal"}), None)
    elements = sorted({image.get("alt", "").strip() for image in block["images"]} & ELEMENTS)
    aptitudes = list(dict.fromkeys(APTITUDE_PATTERN.findall(block["text"])))
    effect_text = _effect_text(lines, name)
    keywords = sorted(keyword for keyword in KEYWORDS if effect_text and keyword.casefold() in effect_text.casefold())
    return {
        "printing_id": printing_id,
        "card_base_id": base_card_id(printing_id),
        "rarity": rarity,
        "name_en": name,
        "card_type": card_type,
        "subtype": subtype,
        "color": color,
        "cost": _number_after_prefix(lines, ("Cost ",)),
        "power_or_durability": _number_after_prefix(lines, ("Power ", "Durability ")),
        "strike": _number_after_prefix(lines, ("Strike ",)),
        "elements": elements,
        "aptitudes": aptitudes,
        "keywords": keywords,
        "effect_text_en": effect_text,
        "source_url": block["href"],
        "official_image_url": _preferred_card_image(block["images"], name),
    }


def parse_japanese_block(block: dict[str, Any]) -> dict[str, Any]:
    lines = _lines(block["text"])
    printing_id = _printing_id(block["text"])
    rarity = _rarity(lines, printing_id)
    name = _name(lines, printing_id, rarity)
    return {
        "printing_id": printing_id,
        "name_ja": name,
        "effect_text_ja": _effect_text(lines, name),
        "source_url_ja": block["href"],
    }


async def extract_blocks(page: Page, url: str, expected_printings: int) -> list[dict[str, Any]]:
    await page.goto(url, wait_until="domcontentloaded")
    await page.wait_for_function(
        """expected => {
            const matches = document.body.innerText.match(/EBP01-\d{3}(?:SSP|OSR|SP|SR)?/g) || [];
            return new Set(matches).size >= expected;
        }""",
        expected_printings,
        timeout=90000,
    )
    raw_blocks = await page.evaluate(
        """() => {
            const links = Array.from(document.querySelectorAll('a')).filter(link =>
                link.textContent.trim().toUpperCase() === 'MORE' && link.href.includes('/cardlist/detail')
            );
            return links.map(link => {
                let node = link;
                let best = link.parentElement;
                while (node.parentElement) {
                    const candidate = node.parentElement;
                    const matches = candidate.innerText.match(/EBP01-\d{3}(?:SSP|OSR|SP|SR)?/g) || [];
                    const unique = new Set(matches);
                    if (unique.size === 1) {
                        best = candidate;
                        node = candidate;
                        continue;
                    }
                    if (unique.size > 1) break;
                    node = candidate;
                }
                const images = Array.from(best.querySelectorAll('img')).map(image => ({
                    src: image.currentSrc || image.src || image.getAttribute('data-src') || '',
                    alt: image.alt || '',
                    area: (image.naturalWidth || image.width || 0) * (image.naturalHeight || image.height || 0),
                }));
                return {text: best.innerText, href: link.href, images};
            });
        }"""
    )
    deduplicated: dict[str, dict[str, Any]] = {}
    for block in raw_blocks:
        deduplicated[_printing_id(block["text"])] = block
    blocks = [deduplicated[key] for key in sorted(deduplicated)]
    if len(blocks) != expected_printings:
        raise ValueError(f"Expected {expected_printings} official printings at {url}, got {len(blocks)}")
    return blocks


def _field_provenance(
    entity_type: str,
    entity_id: str,
    payload: dict[str, Any],
    source_url: str,
    retrieved_at: str,
) -> list[dict[str, Any]]:
    records = []
    ignored = {"source_url", "source_url_en", "source_url_ja", "source_checked_at"}
    for field, value in payload.items():
        if field in ignored:
            continue
        records.append(
            ProvenanceRecord(
                entity_type=entity_type,
                entity_id=entity_id,
                field=field,
                value=value,
                source_url=source_url,
                retrieved_at=retrieved_at,
                source_type="official",
                verification_status="verified_official",
            ).model_dump()
        )
    return records


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
        if not printing_id.startswith("EBP01-") or printing_id not in printings_by_id:
            continue
        printing = printings_by_id[printing_id]
        card = cards_by_id[printing.card_base_id]
        for field, getter in field_map.items():
            if field not in seed:
                continue
            official_value = getter(card, printing)
            community_value = seed[field]
            if community_value == official_value:
                status = "matched_official"
            else:
                status = "mismatch_official_wins"
                mismatches.append(
                    {
                        "printing_id": printing_id,
                        "field": field,
                        "official_value": official_value,
                        "community_value": community_value,
                    }
                )
            provenance.append(
                ProvenanceRecord(
                    entity_type="printing",
                    entity_id=printing_id,
                    field=field,
                    value=community_value,
                    source_url=COMMUNITY_JSON_URL,
                    retrieved_at=retrieved_at,
                    source_type="community_seed",
                    verification_status=status,
                ).model_dump()
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
        browser = await playwright.chromium.launch()
        en_page = await browser.new_page()
        ja_page = await browser.new_page()
        en_blocks, ja_blocks = await asyncio.gather(
            extract_blocks(en_page, EN_LIST_URL, expected_printings),
            extract_blocks(ja_page, JA_LIST_URL, expected_printings),
        )
        request = await playwright.request.new_context()
        community_response = await request.get(COMMUNITY_JSON_URL)
        if not community_response.ok:
            raise ValueError(f"Community seed fetch failed: HTTP {community_response.status}")
        community = await community_response.json()
        await request.dispose()
        await browser.close()

    en_rows = {row["printing_id"]: row for row in (parse_english_block(block) for block in en_blocks)}
    ja_rows = {row["printing_id"]: row for row in (parse_japanese_block(block) for block in ja_blocks)}
    if set(en_rows) != set(ja_rows):
        missing_ja = sorted(set(en_rows) - set(ja_rows))
        missing_en = sorted(set(ja_rows) - set(en_rows))
        raise ValueError(f"Japanese/English printing mismatch: missing_ja={missing_ja}, missing_en={missing_en}")

    cards: list[PalworldCard] = []
    printings: list[PalworldPrinting] = []
    provenance: list[dict[str, Any]] = []
    base_rows = [row for printing_id, row in en_rows.items() if printing_id == row["card_base_id"]]
    for row in sorted(base_rows, key=lambda item: item["card_base_id"]):
        ja = ja_rows[row["printing_id"]]
        card = PalworldCard(
            card_base_id=row["card_base_id"],
            name_ja=ja["name_ja"],
            name_en=row["name_en"],
            card_type=row["card_type"],
            subtype=row["subtype"],
            color=row["color"],
            cost=row["cost"],
            power_or_durability=row["power_or_durability"],
            strike=row["strike"],
            elements=row["elements"],
            aptitudes=row["aptitudes"],
            keywords=row["keywords"],
            effect_text_ja=ja["effect_text_ja"],
            effect_text_en=row["effect_text_en"],
            product_code="EBP01",
            source_url_ja=ja["source_url_ja"],
            source_url_en=row["source_url"],
            source_checked_at=retrieved_at,
        )
        cards.append(card)
        en_payload = card.model_dump(exclude={"name_ja", "effect_text_ja", "source_url_ja"})
        provenance.extend(_field_provenance("card", card.card_base_id, en_payload, row["source_url"], retrieved_at))
        ja_payload = {"name_ja": card.name_ja, "effect_text_ja": card.effect_text_ja}
        provenance.extend(_field_provenance("card", card.card_base_id, ja_payload, ja["source_url_ja"], retrieved_at))

    for printing_id, row in sorted(en_rows.items()):
        printing = PalworldPrinting(
            printing_id=printing_id,
            card_base_id=row["card_base_id"],
            rarity=row["rarity"],
            is_parallel=printing_id != row["card_base_id"],
            official_image_url=row["official_image_url"],
            source_url=row["source_url"],
            source_checked_at=retrieved_at,
        )
        printings.append(printing)
        provenance.extend(
            _field_provenance("printing", printing_id, printing.model_dump(), row["source_url"], retrieved_at)
        )

    cards, printings = validate_snapshot(
        cards,
        printings,
        expected_cards=expected_cards,
        expected_printings=expected_printings,
    )
    mismatches, community_provenance = compare_community_seed(community, cards, printings, retrieved_at)
    provenance.extend(community_provenance)
    provenance.sort(key=lambda row: (row["entity_type"], row["entity_id"], row["field"], row["source_type"]))

    manifest = {
        "schema_version": 1,
        "product_code": "EBP01",
        "logical_card_count": len(cards),
        "printing_count": len(printings),
        "source_checked_at": retrieved_at,
        "official_sources": {
            "english_card_list": EN_LIST_URL,
            "japanese_card_list": JA_LIST_URL,
            "english_product": EN_PRODUCT_URL,
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
        "community_mismatch_count": len(mismatches),
        "community_mismatches": mismatches,
        "policy": "Official Palworld OCG data wins over community seed on every canonical field.",
    }
    _write_json(output_dir / "cards.json", [card.model_dump() for card in cards])
    _write_json(output_dir / "printings.json", [printing.model_dump() for printing in printings])
    _write_json(output_dir / "provenance.json", provenance)
    _write_json(output_dir / "audit.json", audit)
    _write_json(output_dir / "manifest.json", manifest)


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Palworld OCG BP01 from official card lists")
    parser.add_argument("--output", type=Path, default=Path("data/palworld/bp01"))
    parser.add_argument("--expected-cards", type=int, default=100)
    parser.add_argument("--expected-printings", type=int, default=161)
    args = parser.parse_args()
    asyncio.run(import_bp01(args.output, args.expected_cards, args.expected_printings))


if __name__ == "__main__":
    main()
