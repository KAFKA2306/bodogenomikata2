from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_DIR = ROOT / "ontology" / "murder-mystery"


class OntologyValidationError(ValueError):
    pass


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise OntologyValidationError(f"{path} must contain a mapping")
    return data


def require(condition: bool, message: str) -> None:
    if not condition:
        raise OntologyValidationError(message)


def concept_ids(vocabulary: dict[str, Any], scheme: str) -> set[str]:
    schemes = vocabulary.get("concept_schemes", {})
    require(scheme in schemes, f"missing concept scheme: {scheme}")
    concepts = schemes[scheme].get("concepts", {})
    require(isinstance(concepts, dict) and concepts, f"empty concept scheme: {scheme}")
    return set(concepts)


def validate_collection_policy(core: dict[str, Any]) -> None:
    policy = core.get("collection_policy", {})
    allowed = set(policy.get("allowed_methods", []))
    prohibited = set(policy.get("prohibited_methods", []))
    require(
        allowed == {"manual_entry", "official_api", "creator_submission", "seller_export"},
        "collection_policy.allowed_methods must stay explicit and closed",
    )
    require(
        {"scraping", "crawling", "automated_html_extraction"} <= prohibited,
        "scraping, crawling, and automated HTML extraction must remain prohibited",
    )


def validate_source_mappings(mappings: dict[str, Any]) -> None:
    allowed_methods = {"manual_entry", "official_api", "creator_submission", "seller_export"}
    sources = mappings.get("sources", {})
    require(isinstance(sources, dict) and sources, "source mappings must define sources")
    for source_id, source in sources.items():
        method = source.get("defaultAcquisitionMethod")
        require(method in allowed_methods, f"{source_id}: invalid acquisition method {method!r}")
        if source.get("sourceType") in {"secondary_information_site", "platform_official"}:
            require(
                source.get("automationStatus") != "enabled",
                f"{source_id}: automation cannot be enabled without a verified official API or permission",
            )


def validate_example(example: dict[str, Any], vocabulary: dict[str, Any]) -> None:
    require(example.get("type") == "ScenarioWork", "example.type must be ScenarioWork")
    require(bool(example.get("canonicalTitle")), "canonicalTitle is required")

    source_records = example.get("sourceRecords", [])
    source_ids = {record.get("id") for record in source_records}
    require(None not in source_ids and source_ids, "source records require IDs")

    acquisition_ids = concept_ids(vocabulary, "acquisitionMethod")
    source_type_ids = concept_ids(vocabulary, "sourceType")
    rights_ids = concept_ids(vocabulary, "rightsStatus")
    verification_ids = concept_ids(vocabulary, "verificationStatus")
    gm_ids = concept_ids(vocabulary, "gmRequirement")
    play_mode_ids = concept_ids(vocabulary, "playMode")
    edition_type_ids = concept_ids(vocabulary, "editionType")
    price_basis_ids = concept_ids(vocabulary, "priceBasis")
    availability_ids = concept_ids(vocabulary, "availability")
    spoiler_ids = concept_ids(vocabulary, "spoilerLevel")

    for record in source_records:
        require(record["acquiredBy"] in acquisition_ids, f"invalid acquiredBy: {record['acquiredBy']}")
        require(record["sourceType"] in source_type_ids, f"invalid sourceType: {record['sourceType']}")
        require(record["rightsStatus"] in rights_ids, f"invalid rightsStatus: {record['rightsStatus']}")
        require(
            record["verificationStatus"] in verification_ids,
            f"invalid verificationStatus: {record['verificationStatus']}",
        )

    editions = example.get("editions", [])
    require(editions, "at least one edition is required")
    for edition in editions:
        require(edition.get("editionType") in edition_type_ids, "invalid editionType")
        for source_id in edition.get("sourceRecords", []):
            require(source_id in source_ids, f"unknown edition source record: {source_id}")
        configs = edition.get("playConfigurations", [])
        require(configs, f"{edition.get('id')}: at least one play configuration is required")
        for config in configs:
            require(config["minimumPlayers"] <= config["maximumPlayers"], "player range is reversed")
            require(
                config["minimumDurationMinutes"] <= config["maximumDurationMinutes"],
                "duration range is reversed",
            )
            require(config["gmRequirement"] in gm_ids, "invalid gmRequirement")
            require(set(config["playModes"]) <= play_mode_ids, "invalid playMode")
        for offer in edition.get("offers", []):
            require(offer["availability"] in availability_ids, "invalid availability")
            require(offer.get("sourceRecord") in source_ids, "offer references unknown source")
            if "price" in offer:
                require(bool(offer.get("currency")), "priced offer requires currency")
                require(offer.get("priceBasis") in price_basis_ids, "priced offer requires priceBasis")

    for assertion in example.get("assertions", []):
        require(assertion.get("assertedBy") in source_ids, "assertion references unknown source")
        confidence = assertion.get("confidence")
        require(isinstance(confidence, (int, float)) and 0 <= confidence <= 1, "confidence must be 0..1")
        require(assertion.get("verificationStatus") in verification_ids, "invalid assertion verificationStatus")

    spoiler_level = example.get("spoilerClassification")
    require(spoiler_level in spoiler_ids, "invalid spoilerClassification")
    require(
        spoiler_level in {"none", "premise", "character_public"},
        "public example must not contain minor, major, or solution spoilers",
    )


def validate_repository(root: Path = ROOT) -> None:
    ontology_dir = root / "ontology" / "murder-mystery"
    core = load_yaml(ontology_dir / "core.yaml")
    vocabulary = load_yaml(ontology_dir / "vocabulary.yaml")
    mappings = load_yaml(ontology_dir / "source-mappings.yaml")
    example = load_yaml(ontology_dir / "example-record.yaml")

    with (ontology_dir / "record.schema.json").open(encoding="utf-8") as handle:
        schema = json.load(handle)
    require(
        schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
        "unexpected JSON Schema dialect",
    )

    validate_collection_policy(core)
    validate_source_mappings(mappings)
    validate_example(example, vocabulary)


def main() -> int:
    validate_repository()
    print("murder-mystery ontology: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
