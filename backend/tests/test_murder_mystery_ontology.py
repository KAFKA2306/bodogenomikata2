from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "scripts" / "validate_murder_mystery_ontology.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_murder_mystery_ontology", VALIDATOR_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_murder_mystery_ontology_is_valid() -> None:
    validator = load_validator()
    validator.validate_repository(ROOT)
