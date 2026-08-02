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


def test_scaffolder_creates_one_stable_human_workspace(tmp_path: Path) -> None:
    creator = load_module(
        "create_original_murder_mystery",
        ROOT / "scripts" / "create_original_murder_mystery.py",
    )
    validator = load_module(
        "validate_original_murder_mystery_workspace",
        ROOT / "scripts" / "validate_original_murder_mystery_workspace.py",
    )
    shutil.copytree(ROOT / "works", tmp_path / "works")
    (tmp_path / ".gitignore").write_text(
        "works/murder-mystery/projects/*/private/\n",
        encoding="utf-8",
    )

    project_dir = creator.create_project(tmp_path, "human-seed-test", "人間の素案テスト")
    project = yaml.safe_load((project_dir / "project.yaml").read_text(encoding="utf-8"))

    assert project_dir == tmp_path / "works/murder-mystery/projects/human-seed-test"
    assert project["id"] == "original-mm:human-seed-test"
    assert project["status"] == "seed"
    assert project["authorship"]["canonicalPlotGeneratedByAI"] is False
    assert (project_dir / "README.md").is_file()
    assert (project_dir / "private/WORK.md").is_file()
    assert (project_dir / "private/PLAYTESTS.md").is_file()
    assert not (project_dir / "design").exists()

    project["status"] = "playtesting"
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(project, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    validator.validate_workspace(tmp_path)
    assert project_dir == tmp_path / "works/murder-mystery/projects/human-seed-test"
