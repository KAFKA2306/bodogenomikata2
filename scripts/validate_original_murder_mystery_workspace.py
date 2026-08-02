from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "works" / "murder-mystery"
INDEX_PATH = WORKSPACE / "index.yaml"
REQUIRED_TEMPLATE_FILES = {
    "project.yaml",
    "design/00-human-seed.md",
    "design/10-creative-thesis.md",
    "design/20-characters.yaml",
    "design/30-plot-beats.yaml",
    "design/40-mystery-and-experience.yaml",
    "design/50-originality-audit.md",
    "playtest/session.md",
    "private/README.md",
}
REQUIRED_HUMAN_DECISIONS = {
    "humanSeed",
    "ethicalContradiction",
    "characterLivesAndWants",
    "truthAndCausality",
    "centralSurprise",
    "climaxChoice",
    "ending",
    "finalProseAndDialogue",
}


class WorkspaceValidationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise WorkspaceValidationError(message)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    require(isinstance(value, dict), f"YAML root must be a mapping: {path}")
    return value


def tracked_private_paths(root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "works/murder-mystery"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
    return [line for line in result.stdout.splitlines() if "/private/" in line and "/_templates/" not in line]


def validate_project(project_dir: Path, stage_name: str, stage_status: str, required_files: list[str]) -> None:
    for relative in required_files:
        require((project_dir / relative).is_file(), f"{project_dir}: missing {relative}")

    project = load_yaml(project_dir / "project.yaml")
    require(project.get("slug") == project_dir.name, f"{project_dir}: slug must match directory name")
    require(project.get("status") == stage_status, f"{project_dir}: status must match {stage_name}")
    require(project.get("id") == f"original-mm:{project_dir.name}", f"{project_dir}: invalid project id")

    authorship = project.get("authorship", {})
    require(authorship.get("canonicalPlotGeneratedByAI") is False, f"{project_dir}: AI canonical plot is prohibited")
    decisions = authorship.get("requiredHumanDecisions", {})
    require(set(decisions) == REQUIRED_HUMAN_DECISIONS, f"{project_dir}: human decision keys are incomplete")

    privacy = project.get("privacy", {})
    require(
        privacy.get("spoilerMaterialTrackedInThisRepository") is False,
        f"{project_dir}: spoiler material must not be tracked in this repository",
    )
    require(privacy.get("spoilerMaterialLocation") == "private/", f"{project_dir}: private location must be private/")


def validate_workspace(root: Path = ROOT) -> None:
    workspace = root / "works" / "murder-mystery"
    index = load_yaml(workspace / "index.yaml")
    stages = index.get("stages", {})
    require(isinstance(stages, dict) and len(stages) == 6, "workspace must define six lifecycle stages")

    templates = workspace / "_templates"
    for relative in REQUIRED_TEMPLATE_FILES:
        require((templates / relative).is_file(), f"missing template file: {relative}")

    project_template = load_yaml(templates / "project.yaml")
    require(
        project_template.get("authorship", {}).get("canonicalPlotGeneratedByAI") is False,
        "project template must prohibit AI-generated canonical plots",
    )
    require(
        set(project_template.get("authorship", {}).get("requiredHumanDecisions", {})) == REQUIRED_HUMAN_DECISIONS,
        "project template must require all human decisions",
    )

    required_project_files = index.get("requiredProjectFiles", [])
    require(isinstance(required_project_files, list) and required_project_files, "requiredProjectFiles is missing")

    for stage_name, stage in stages.items():
        stage_dir = workspace / stage_name
        require(stage_dir.is_dir(), f"missing stage directory: {stage_name}")
        require((stage_dir / "README.md").is_file(), f"missing stage README: {stage_name}")
        status = stage.get("status")
        require(isinstance(status, str) and status, f"missing stage status: {stage_name}")
        for child in stage_dir.iterdir():
            if child.name == "README.md":
                continue
            require(child.is_dir(), f"unexpected file in stage root: {child}")
            validate_project(child, stage_name, status, required_project_files)

    gitignore = (root / ".gitignore").read_text(encoding="utf-8")
    require(
        "works/murder-mystery/[0-9][0-9]-*/*/private/" in gitignore,
        "project private directories must be ignored",
    )
    tracked = tracked_private_paths(root)
    require(not tracked, f"private spoiler files are tracked: {tracked}")


def main() -> int:
    validate_workspace()
    print("original murder-mystery workspace: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
