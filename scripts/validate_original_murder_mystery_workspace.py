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
    "README.md",
    "private/WORK.md",
    "private/PLAYTESTS.md",
}
REQUIRED_TRACKED_PROJECT_FILES = {"project.yaml", "README.md"}
REQUIRED_TRACKED_SPOILER_FILES = {
    "private/START_HERE.md",
    "private/PLAY_PACKAGE.md",
    "private/GM_GUIDE.md",
    "private/CARDS.md",
    "private/PLAYTESTS.md",
}
REQUIRED_HUMAN_DECISIONS = {
    "human_seed",
    "ethical_contradiction",
    "character_lives_and_wants",
    "truth_and_causality",
    "central_surprise",
    "climax_choice",
    "ending",
    "final_prose_and_dialogue",
}
LEGACY_DIRECTORIES = {
    "00-inbox",
    "10-incubating",
    "20-developing",
    "30-playtesting",
    "40-production",
    "90-archived",
    "_templates",
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
            ["git", "ls-files", "works/murder-mystery/projects"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
    return [line for line in result.stdout.splitlines() if "/private/" in line]


def validate_project(project_dir: Path, statuses: set[str]) -> bool:
    for filename in REQUIRED_TRACKED_PROJECT_FILES:
        require((project_dir / filename).is_file(), f"{project_dir}: missing {filename}")

    visible_names = {path.name for path in project_dir.iterdir()}
    require(
        visible_names <= {"project.yaml", "README.md", "private"},
        f"{project_dir}: keep the project root minimal; unexpected entries: "
        f"{sorted(visible_names - {'project.yaml', 'README.md', 'private'})}",
    )

    project = load_yaml(project_dir / "project.yaml")
    require(project.get("schemaVersion") == 2, f"{project_dir}: schemaVersion must be 2")
    require(project.get("slug") == project_dir.name, f"{project_dir}: slug must match directory name")
    require(project.get("id") == f"original-mm:{project_dir.name}", f"{project_dir}: invalid project id")
    require(project.get("status") in statuses, f"{project_dir}: unknown status {project.get('status')!r}")
    require(bool(project.get("title")), f"{project_dir}: title is required")

    authorship = project.get("authorship", {})
    require(
        authorship.get("canonicalPlotGeneratedByAI") is False,
        f"{project_dir}: AI-generated canonical plots are prohibited",
    )

    privacy = project.get("privacy", {})
    require(privacy.get("spoilerMaterialLocation") == "private/", f"{project_dir}: private location must be private/")

    tracked_spoilers = privacy.get("spoilerMaterialTrackedInThisRepository") is True
    if tracked_spoilers:
        require(privacy.get("trackedSpoilers") is True, f"{project_dir}: trackedSpoilers opt-in is required")
        require(
            privacy.get("publicationApprovedByOwner") is True,
            f"{project_dir}: owner approval is required before tracking spoilers",
        )
        for relative in REQUIRED_TRACKED_SPOILER_FILES:
            require((project_dir / relative).is_file(), f"{project_dir}: tracked spoiler workspace is missing {relative}")
    else:
        require(
            privacy.get("trackedSpoilers") is not True,
            f"{project_dir}: trackedSpoilers cannot be true while repository tracking is false",
        )
        private_dir = project_dir / "private"
        if private_dir.exists():
            require(private_dir.is_dir(), f"{project_dir}: private must be a directory")
            for filename in ("WORK.md", "PLAYTESTS.md"):
                require((private_dir / filename).is_file(), f"{project_dir}: local private workspace is missing {filename}")

    return tracked_spoilers


def validate_workspace(root: Path = ROOT) -> None:
    workspace = root / "works" / "murder-mystery"
    index = load_yaml(workspace / "index.yaml")
    require(index.get("schemaVersion") == 2, "workspace schemaVersion must be 2")
    require(index.get("projectRoot") == "works/murder-mystery/projects", "projectRoot must be stable")
    require(index.get("templateRoot") == "works/murder-mystery/_template", "templateRoot must be _template")

    statuses_mapping = index.get("statuses", {})
    require(isinstance(statuses_mapping, dict) and statuses_mapping, "statuses are required")
    statuses = set(statuses_mapping)
    require(statuses == {"seed", "developing", "playtesting", "production", "archived"}, "unexpected statuses")

    for name in LEGACY_DIRECTORIES:
        require(not (workspace / name).exists(), f"legacy over-segmented directory must be removed: {name}")

    templates = workspace / "_template"
    for relative in REQUIRED_TEMPLATE_FILES:
        require((templates / relative).is_file(), f"missing template file: {relative}")

    project_template = load_yaml(templates / "project.yaml")
    require(project_template.get("schemaVersion") == 2, "project template schemaVersion must be 2")
    require(
        project_template.get("authorship", {}).get("canonicalPlotGeneratedByAI") is False,
        "project template must prohibit AI-generated canonical plots",
    )

    work_template = (templates / "private" / "WORK.md").read_text(encoding="utf-8")
    for heading in ("人間の原点", "創作命題", "人物", "起承転結", "驚き", "結末", "次の一手"):
        require(heading in work_template, f"WORK.md template is missing section: {heading}")

    projects = workspace / "projects"
    require(projects.is_dir(), "projects directory is required")
    require((projects / "README.md").is_file(), "projects/README.md is required")

    tracked_spoiler_slugs: set[str] = set()
    for child in projects.iterdir():
        if child.name == "README.md":
            continue
        require(child.is_dir(), f"unexpected file in projects root: {child}")
        if validate_project(child, statuses):
            tracked_spoiler_slugs.add(child.name)

    gitignore = (root / ".gitignore").read_text(encoding="utf-8")
    default_ignore = "works/murder-mystery/projects/*/private/"
    require(default_ignore in gitignore, "project private directories must be ignored by default")

    for slug in tracked_spoiler_slugs:
        require(
            f"!works/murder-mystery/projects/{slug}/private/" in gitignore,
            f"{slug}: private directory must be explicitly unignored",
        )
        require(
            f"!works/murder-mystery/projects/{slug}/private/**" in gitignore,
            f"{slug}: private contents must be explicitly unignored",
        )

    tracked = tracked_private_paths(root)
    allowed_prefixes = {
        f"works/murder-mystery/projects/{slug}/private/" for slug in tracked_spoiler_slugs
    }
    unexpected = [
        path
        for path in tracked
        if not any(path.startswith(prefix) for prefix in allowed_prefixes)
    ]
    require(not unexpected, f"private spoiler files are tracked without owner-approved opt-in: {unexpected}")

    policy = index.get("humanAuthorshipPolicy", {})
    require(policy.get("canonicalPlotGenerationByAI") == "prohibited", "AI plot generation policy must be prohibited")
    require(set(policy.get("requiredHumanDecisions", [])) == REQUIRED_HUMAN_DECISIONS, "human decision policy is incomplete")


def main() -> int:
    validate_workspace()
    print("original murder-mystery workspace: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
