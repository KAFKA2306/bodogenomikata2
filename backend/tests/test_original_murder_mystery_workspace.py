from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_repository_workspace_is_valid() -> None:
    validator = load_module(
        "validate_original_murder_mystery_workspace",
        ROOT / "scripts" / "validate_original_murder_mystery_workspace.py",
    )
    validator.validate_workspace(ROOT)


def test_scaffolder_creates_human_led_project(tmp_path: Path) -> None:
    creator = load_module(
        "create_original_murder_mystery",
        ROOT / "scripts" / "create_original_murder_mystery.py",
    )
    shutil.copytree(ROOT / "works", tmp_path / "works")
    (tmp_path / ".gitignore").write_text(
        "works/murder-mystery/[0-9][0-9]-*/*/private/\n",
        encoding="utf-8",
    )

    project_dir = creator.create_project(tmp_path, "human-seed-test", "人間の素案テスト")
    project = yaml.safe_load((project_dir / "project.yaml").read_text(encoding="utf-8"))

    assert project_dir == tmp_path / "works/murder-mystery/00-inbox/human-seed-test"
    assert project["id"] == "original-mm:human-seed-test"
    assert project["status"] == "inbox"
    assert project["authorship"]["canonicalPlotGeneratedByAI"] is False
    assert (project_dir / "design/00-human-seed.md").is_file()
    assert (project_dir / "private/README.md").is_file()
