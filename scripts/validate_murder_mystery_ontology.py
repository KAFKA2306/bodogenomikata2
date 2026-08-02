from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_DIR = ROOT / "ontology" / "murder-mystery"
CANDIDATE_CORPUS = ROOT / "data" / "murder-mystery" / "popular-100-candidates.yaml"


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


def normalized_title(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    return re.sub(r"\s+", " ", normalized).strip().casefold()


def is_https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


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


def validate_candidate_corpus(corpus: dict[str, Any]) -> None:
    metadata = corpus.get("metadata", {})
    works = corpus.get("works", [])
    require(metadata.get("status") == "candidate_corpus", "candidate corpus status must be explicit")
    require(metadata.get("recordCount") == 100, "candidate corpus metadata.recordCount must be 100")
    require(isinstance(works, list) and len(works) == 100, "candidate corpus must contain exactly 100 works")
    require(
        metadata.get("rankingPolicy") and "順位を付けない" in metadata["rankingPolicy"],
        "candidate corpus must not imply an unsupported popularity ranking",
    )
    require(metadata.get("collectionMethod") == "manual_entry_from_public_source_manifests", "invalid collection method")
    require(metadata.get("spoilerLevel") == "none", "candidate corpus must be spoiler-free")

    manifests = metadata.get("sourceManifests", [])
    require(isinstance(manifests, list) and len(manifests) >= 3, "at least three source manifests are required")
    manifest_types = {manifest.get("sourceType") for manifest in manifests}
    require("creator_official" in manifest_types, "creator official evidence is required")
    require("secondary_information_site" in manifest_types, "secondary source evidence is required")
    for manifest in manifests:
        require(is_https_url(manifest.get("url")), f"invalid source manifest URL: {manifest.get('name')}")

    expected_ids = {f"mmc-{number:03d}" for number in range(1, 101)}
    actual_ids = {work.get("id") for work in works}
    require(actual_ids == expected_ids, "candidate IDs must be the complete mmc-001..mmc-100 sequence")

    normalized_titles: set[str] = set()
    distribution_evidence_count = 0
    manifest_only_count = 0
    forbidden_fields = {
        "rank",
        "score",
        "rating",
        "reviewBody",
        "culprit",
        "secrets",
        "privateObjectives",
        "handoutBody",
        "truth",
        "endingDetails",
    }

    for work in works:
        title = work.get("title")
        require(isinstance(title, str) and title.strip(), f"{work.get('id')}: title is required")
        normalized = normalized_title(title)
        require(normalized not in normalized_titles, f"duplicate normalized title: {title}")
        normalized_titles.add(normalized)

        require(work.get("selectionStatus") == "candidate", f"{work.get('id')}: selectionStatus must be candidate")
        require(
            work.get("popularityStatus") == "unranked_candidate",
            f"{work.get('id')}: popularityStatus must remain unranked_candidate",
        )
        require(not (forbidden_fields & set(work)), f"{work.get('id')}: forbidden unverified or spoiler fields present")

        evidence = work.get("evidence", [])
        require(isinstance(evidence, list) and evidence, f"{work.get('id')}: evidence is required")
        evidence_types = set()
        for item in evidence:
            require(isinstance(item, dict), f"{work.get('id')}: evidence item must be a mapping")
            require(is_https_url(item.get("url")), f"{work.get('id')}: evidence URL must be HTTPS")
            evidence_types.add(item.get("type"))

        require(
            "source_manifest" in evidence_types or "creator_official_catalog" in evidence_types,
            f"{work.get('id')}: source manifest evidence is required",
        )
        if {"distribution_or_official_page", "distribution_or_platform_page"} & evidence_types:
            distribution_evidence_count += 1
        else:
            manifest_only_count += 1
            require(
                work.get("verificationStatus") == "source_manifest_only",
                f"{work.get('id')}: manifest-only records must be labeled source_manifest_only",
            )

    require(distribution_evidence_count >= 90, "at least 90 works must include a distribution or platform URL")
    require(manifest_only_count <= 10, "too many source-manifest-only works")


def validate_repository(root: Path = ROOT) -> None:
    ontology_dir = root / "ontology" / "murder-mystery"
    core = load_yaml(ontology_dir / "core.yaml")
    vocabulary = load_yaml(ontology_dir / "vocabulary.yaml")
    mappings = load_yaml(ontology_dir / "source-mappings.yaml")
    example = load_yaml(ontology_dir / "example-record.yaml")
    candidate_corpus = load_yaml(root / "data" / "murder-mystery" / "popular-100-candidates.yaml")

    with (ontology_dir / "record.schema.json").open(encoding="utf-8") as handle:
        schema = json.load(handle)
    require(
        schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
        "unexpected JSON Schema dialect",
    )

    validate_collection_policy(core)
    validate_source_mappings(mappings)
    validate_example(example, vocabulary)
    validate_candidate_corpus(candidate_corpus)


def main() -> int:
    validate_repository()
    print("murder-mystery ontology and 100-work candidate corpus: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
