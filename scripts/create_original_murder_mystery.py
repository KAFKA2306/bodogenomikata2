from __future__ import annotations

import argparse
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = Path("works/murder-mystery")
PROJECT_ROOT = WORKSPACE / "projects"
TEMPLATE_ROOT = WORKSPACE / "_template"
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class WorkspaceCreationError(ValueError):
    pass


def _load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise WorkspaceCreationError(f"template must be a mapping: {path}")
    return value


def _write_yaml(path: Path, value: dict) -> None:
    path.write_text(
        yaml.safe_dump(value, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def _render_template(path: Path, title: str, slug: str) -> None:
    rendered = path.read_text(encoding="utf-8").replace("{{ title }}", title).replace("{{ slug }}", slug)
    path.write_text(rendered, encoding="utf-8")


def create_project(root: Path, slug: str, title: str) -> Path:
    if not SLUG_PATTERN.fullmatch(slug):
        raise WorkspaceCreationError("slug must use lowercase ASCII letters, numbers, and single hyphens")
    title = title.strip()
    if not title:
        raise WorkspaceCreationError("title must not be empty")

    templates = root / TEMPLATE_ROOT
    target = root / PROJECT_ROOT / slug
    if target.exists():
        raise WorkspaceCreationError(f"project already exists: {target}")

    required_templates = (
        templates / "project.yaml",
        templates / "README.md",
        templates / "private" / "WORK.md",
        templates / "private" / "PLAYTESTS.md",
    )
    for required in required_templates:
        if not required.is_file():
            raise WorkspaceCreationError(f"missing template file: {required}")

    shutil.copytree(templates, target)

    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    project = _load_yaml(target / "project.yaml")
    project.update(
        {
            "id": f"original-mm:{slug}",
            "slug": slug,
            "title": title,
            "status": "seed",
            "createdAt": now,
            "updatedAt": now,
        }
    )
    _write_yaml(target / "project.yaml", project)

    for path in (target / "README.md", target / "private" / "WORK.md", target / "private" / "PLAYTESTS.md"):
        _render_template(path, title, slug)

    return target


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a minimal human-led original murder-mystery project")
    parser.add_argument("slug")
    parser.add_argument("title")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    target = create_project(ROOT, args.slug, args.title)
    print(target.relative_to(ROOT))
    print(f"next: edit {target.relative_to(ROOT) / 'private' / 'WORK.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
