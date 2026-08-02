from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_DIR = ROOT / "ontology" / "murder-mystery"

CREATIVE_ONTOLOGY = ONTOLOGY_DIR / "creative-analysis.yaml"
CREATIVE_VOCABULARY = ONTOLOGY_DIR / "creative-vocabulary.yaml"
CREATIVE_SCHEMA = ONTOLOGY_DIR / "creative-analysis.schema.json"
CREATIVE_EXAMPLE = ONTOLOGY_DIR / "creative-analysis.example.yaml"

PUBLIC_SPOILER_LEVELS = {"none", "premise", "character_public"}
FORBIDDEN_AUTHORSHIP_CLAIMS = {
    "human_authored",
    "ai_authored",
    "ai_generated_probability",
    "humanAuthoredProbability",
    "aiAuthoredProbability",
}
EXECUTION_ONLY_CONCEPTS = {
    "foreshadowing_fairness",
    "reveal_timing",
    "reinterpretation_power",
    "emotional_consequence",
    "gimmick_dependency",
    "predictability_control",
    "attachment_formation",
    "earned_emotion",
    "choice_responsibility",
    "relationship_payoff",
    "loss_irreversibility",
    "restraint",
    "catharsis",
    "aftertaste_duration",
    "ending_integration",
}
EXECUTION_EVIDENCE_LEVELS = {"full_play", "authorized_text"}


class CreativeOntologyValidationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CreativeOntologyValidationError(message)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    require(isinstance(data, dict), f"{path} must contain a mapping")
    return data


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    require(isinstance(data, dict), f"{path} must contain an object")
    return data


def concept_ids(vocabulary: dict[str, Any], scheme: str) -> set[str]:
    schemes = vocabulary.get("concept_schemes", {})
    require(scheme in schemes, f"missing creative concept scheme: {scheme}")
    concepts = schemes[scheme].get("concepts", {})
    require(isinstance(concepts, dict) and concepts, f"empty creative concept scheme: {scheme}")
    return set(concepts)


def all_concept_ids(vocabulary: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for scheme in vocabulary.get("concept_schemes", {}).values():
        concepts = scheme.get("concepts", {})
        if isinstance(concepts, dict):
            result.update(concepts)
    return result


def validate_research_basis(ontology: dict[str, Any], vocabulary: dict[str, Any]) -> None:
    metadata = ontology.get("metadata", {})
    require(metadata.get("version") == "0.2.0", "creative ontology version must be 0.2.0")
    basis = metadata.get("researchBasis", {})
    require(basis.get("workCount") == 100, "research basis must identify the 100-work corpus")
    require(basis.get("publicDeepDiveCount") == 38, "research basis must identify the 38 public deep dives")

    expected_patterns = {
        "diegetic_form_integration",
        "relationship_as_mechanic",
        "tonal_collision",
        "social_specificity",
        "residual_risk",
        "production_integration",
    }
    require(
        set(basis.get("observedPatternFamilies", [])) == expected_patterns,
        "research basis must preserve the six observed pattern families",
    )
    vocabulary_basis = vocabulary.get("metadata", {}).get("researchBasis", {})
    require(vocabulary_basis.get("workCount") == 100, "creative vocabulary must identify the 100-work corpus")
    require(
        vocabulary_basis.get("publicDeepDiveCount") == 38,
        "creative vocabulary must identify the 38 public deep dives",
    )


def validate_structure(ontology: dict[str, Any], vocabulary: dict[str, Any]) -> None:
    required_classes = {
        "CreativeProfile",
        "CreativeObservation",
        "CreativeEvidence",
        "CreativeSignature",
        "SurpriseDesign",
        "EmotionalDesign",
        "ProductionIntegration",
        "CorpusDiversityObservation",
        "CreativeAssessmentProtocol",
        "ProductionCredit",
    }
    classes = ontology.get("classes", {})
    require(required_classes <= set(classes), "creative ontology is missing required classes")

    required_schemes = {
        "evidenceLevel",
        "claimMode",
        "creativeOperation",
        "humanTextureSignal",
        "surpriseMechanism",
        "surpriseQuality",
        "emotionalMechanism",
        "emotionalQuality",
        "productionIntegration",
        "assessmentStrength",
        "polarity",
        "replaceability",
        "craftSignal",
        "originalitySignal",
        "breadthSignal",
        "emotionTone",
    }
    schemes = vocabulary.get("concept_schemes", {})
    require(required_schemes <= set(schemes), "creative vocabulary is missing required concept schemes")

    human_texture = ontology.get("dimensions", {}).get("perceivedHumanTexture", {})
    require(
        FORBIDDEN_AUTHORSHIP_CLAIMS <= set(human_texture.get("forbiddenClaims", [])),
        "authorship inference must remain explicitly forbidden",
    )

    rule_ids = {rule.get("id") for rule in ontology.get("assessmentRules", [])}
    required_rule_ids = {
        "no-authorship-detection",
        "credits-are-provenance",
        "promise-is-not-execution",
        "execution-evidence-floor",
        "spoiler-isolation",
        "no-popularity-equivalence",
        "edition-specific-assessment",
        "disagreement-preservation",
        "negative-evidence-caution",
        "corpus-scope-explicit",
    }
    require(required_rule_ids <= rule_ids, "creative ontology is missing epistemic guard rules")


def validate_dimension_concepts(ontology: dict[str, Any], vocabulary: dict[str, Any]) -> None:
    scheme_by_dimension = {
        "craft": "craftSignal",
        "creativeOperation": "creativeOperation",
        "originality": "originalitySignal",
        "perceivedHumanTexture": "humanTextureSignal",
        "breadth": "breadthSignal",
    }
    dimensions = ontology.get("dimensions", {})
    for dimension, scheme in scheme_by_dimension.items():
        expected = concept_ids(vocabulary, scheme)
        actual = set(dimensions.get(dimension, {}).get("signals", []))
        require(actual <= expected, f"{dimension} references concepts outside {scheme}")

    require(
        dimensions.get("surpriseDesign", {}).get("mechanismScheme") == "surpriseMechanism",
        "surpriseDesign must use the surpriseMechanism scheme",
    )
    require(
        dimensions.get("surpriseDesign", {}).get("qualityScheme") == "surpriseQuality",
        "surpriseDesign must use the surpriseQuality scheme",
    )
    require(
        dimensions.get("emotionalDesign", {}).get("mechanismScheme") == "emotionalMechanism",
        "emotionalDesign must use the emotionalMechanism scheme",
    )
    require(
        dimensions.get("emotionalDesign", {}).get("qualityScheme") == "emotionalQuality",
        "emotionalDesign must use the emotionalQuality scheme",
    )


def validate_schema(schema: dict[str, Any]) -> None:
    require(
        schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
        "creative schema must use JSON Schema draft 2020-12",
    )
    require(schema.get("properties", {}).get("type", {}).get("const") == "CreativeProfile", "invalid profile type")
    required = set(schema.get("required", []))
    require(
        {"id", "type", "aboutWork", "observations", "assessedAt", "assessor", "publicSpoilerLevel"} <= required,
        "creative schema is missing required profile fields",
    )


def validate_evidence(evidence: dict[str, Any], evidence_levels: set[str]) -> None:
    require(evidence.get("evidenceLevel") in evidence_levels, "invalid evidence level")
    require(evidence.get("accessClass") in {"public", "restricted", "private"}, "invalid access class")
    spoiler_level = evidence.get("spoilerLevel")
    if evidence.get("accessClass") == "public":
        require(spoiler_level in PUBLIC_SPOILER_LEVELS, "public evidence must be spoiler-safe")
    require(bool(evidence.get("sourceRecord")), "creative evidence must reference a SourceRecord")


def validate_example(example: dict[str, Any], vocabulary: dict[str, Any]) -> None:
    require(example.get("type") == "CreativeProfile", "creative example type must be CreativeProfile")
    require(example.get("publicSpoilerLevel") in PUBLIC_SPOILER_LEVELS, "profile public spoiler level is invalid")

    evidence_levels = concept_ids(vocabulary, "evidenceLevel")
    claim_modes = concept_ids(vocabulary, "claimMode")
    strengths = concept_ids(vocabulary, "assessmentStrength")
    polarities = concept_ids(vocabulary, "polarity")
    all_concepts = all_concept_ids(vocabulary)

    observations = example.get("observations", [])
    require(isinstance(observations, list) and observations, "creative example requires observations")
    seen_ids: set[str] = set()
    for observation in observations:
        observation_id = observation.get("id")
        require(observation_id and observation_id not in seen_ids, "creative observation IDs must be unique")
        seen_ids.add(observation_id)

        concept = observation.get("concept")
        evidence_level = observation.get("evidenceLevel")
        claim_mode = observation.get("claimMode")
        require(concept in all_concepts, f"unknown creative concept: {concept}")
        require(evidence_level in evidence_levels, f"invalid observation evidence level: {evidence_level}")
        require(claim_mode in claim_modes, f"invalid claim mode: {claim_mode}")
        require(observation.get("strength") in strengths, "invalid assessment strength")
        require(observation.get("polarity") in polarities, "invalid observation polarity")
        confidence = observation.get("confidence")
        require(isinstance(confidence, (int, float)) and 0 <= confidence <= 1, "confidence must be 0..1")

        if concept in EXECUTION_ONLY_CONCEPTS:
            require(
                evidence_level in EXECUTION_EVIDENCE_LEVELS,
                f"{concept} requires full_play or authorized_text evidence",
            )
        if evidence_level in {"title_only", "public_synopsis", "public_system_description"}:
            require(claim_mode != "executed_assessment", "public surface evidence cannot assert executed quality")

        evidence_items = observation.get("evidence", [])
        require(isinstance(evidence_items, list) and evidence_items, "observation requires evidence")
        for evidence in evidence_items:
            validate_evidence(evidence, evidence_levels)

    serialized = json.dumps(example, ensure_ascii=False)
    for forbidden in FORBIDDEN_AUTHORSHIP_CLAIMS:
        require(forbidden not in serialized, f"forbidden authorship inference present: {forbidden}")

    for design_key in ("surpriseDesign", "emotionalDesign"):
        design = example.get(design_key)
        if not design:
            continue
        require(design.get("claimMode") in claim_modes, f"{design_key}: invalid claimMode")
        require(design.get("evidenceLevel") in evidence_levels, f"{design_key}: invalid evidenceLevel")
        for evidence in design.get("evidence", []):
            validate_evidence(evidence, evidence_levels)

    production_features = concept_ids(vocabulary, "productionIntegration")
    for integration in example.get("productionIntegrations", []):
        require(set(integration.get("features", [])) <= production_features, "unknown production integration feature")
        for evidence in integration.get("evidence", []):
            validate_evidence(evidence, evidence_levels)


def validate_repository(root: Path = ROOT) -> None:
    ontology = load_yaml(root / CREATIVE_ONTOLOGY.relative_to(ROOT))
    vocabulary = load_yaml(root / CREATIVE_VOCABULARY.relative_to(ROOT))
    schema = load_json(root / CREATIVE_SCHEMA.relative_to(ROOT))
    example = load_yaml(root / CREATIVE_EXAMPLE.relative_to(ROOT))

    validate_research_basis(ontology, vocabulary)
    validate_structure(ontology, vocabulary)
    validate_dimension_concepts(ontology, vocabulary)
    validate_schema(schema)
    validate_example(example, vocabulary)


def main() -> int:
    validate_repository()
    print("murder-mystery creative ontology: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
