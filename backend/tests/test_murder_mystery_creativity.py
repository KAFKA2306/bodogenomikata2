from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ANALYZER_PATH = ROOT / "scripts" / "analyze_murder_mystery_creativity.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_murder_mystery_creativity", ANALYZER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_creative_surface_analysis_covers_100_works_without_authorship_inference() -> None:
    analyzer = load_analyzer()
    corpus = analyzer.load_yaml(analyzer.DEFAULT_CORPUS)
    analysis = analyzer.analyze_corpus(corpus)
    analyzer.validate_analysis(analysis)

    assert analysis["metadata"]["recordCount"] == 100
    assert len(analysis["works"]) == 100
    assert analysis["works"][0]["workId"] == "mmc-001"
    assert analysis["works"][-1]["workId"] == "mmc-100"
    assert all(work["evidenceLevel"] == "title_only" for work in analysis["works"])
    assert all("aiAuthored" not in work for work in analysis["works"])
