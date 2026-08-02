from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "scripts" / "validate_murder_mystery_creative_ontology.py"


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_murder_mystery_creative_ontology",
        VALIDATOR_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_creative_ontology_is_research_grounded_and_spoiler_safe() -> None:
    validator = load_validator()
    validator.validate_repository(ROOT)


def test_execution_quality_requires_strong_evidence() -> None:
    validator = load_validator()
    vocabulary = validator.load_yaml(
        ROOT / "ontology" / "murder-mystery" / "creative-vocabulary.yaml"
    )
    invalid = validator.load_yaml(
        ROOT / "ontology" / "murder-mystery" / "creative-analysis.example.yaml"
    )
    invalid["observations"][0]["concept"] = "foreshadowing_fairness"
    invalid["observations"][0]["evidenceLevel"] = "public_synopsis"

    try:
        validator.validate_example(invalid, vocabulary)
    except validator.CreativeOntologyValidationError:
        pass
    else:
        raise AssertionError("execution-only quality was accepted from public synopsis")


def test_authorship_inference_is_rejected() -> None:
    validator = load_validator()
    vocabulary = validator.load_yaml(
        ROOT / "ontology" / "murder-mystery" / "creative-vocabulary.yaml"
    )
    invalid = validator.load_yaml(
        ROOT / "ontology" / "murder-mystery" / "creative-analysis.example.yaml"
    )
    invalid["human_authored"] = True

    try:
        validator.validate_example(invalid, vocabulary)
    except validator.CreativeOntologyValidationError:
        pass
    else:
        raise AssertionError("authorship inference field was accepted")
