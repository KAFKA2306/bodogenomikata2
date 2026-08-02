from __future__ import annotations

import argparse
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = Path("works/murder-mystery")
TEMPLATE_ROOT = WORKSPACE / "_templates"
ALLOWED_STAGES = {
    "00-inbox": "inbox",
    "10-incubating": "incubating",
    "20-developing": "developing",
    "30-playtesting": "playtesting",
    "40-production": "production",
    "90-archived": "archived",
}
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


def create_project(root: Path, slug: str, title: str, stage: str = "00-inbox") -> Path:
    if not SLUG_PATTERN.fullmatch(slug):
        raise WorkspaceCreationError("slug must use lowercase ASCII letters, numbers, and single hyphens")
    if stage not in ALLOWED_STAGES:
        raise WorkspaceCreationError(f"unknown stage: {stage}")
    if not title.strip():
        raise WorkspaceCreationError("title must not be empty")

    workspace = root / WORKSPACE
    templates = root / TEMPLATE_ROOT
    target = workspace / stage / slug
    if target.exists():
        raise WorkspaceCreationError(f"project already exists: {target}")

    for required in (templates / "design", templates / "playtest", templates / "private"):
        if not required.is_dir():
            raise WorkspaceCreationError(f"missing template directory: {required}")

    target.mkdir(parents=True)
    shutil.copytree(templates / "design", target / "design")
    shutil.copytree(templates / "playtest", target / "playtest")
    shutil.copytree(templates / "private", target / "private")
    (target / "public").mkdir()
    (target / "revisions").mkdir()

    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    project = _load_yaml(templates / "project.yaml")
    project.update(
        {
            "id": f"original-mm:{slug}",
            "slug": slug,
            "title": title.strip(),
            "status": ALLOWED_STAGES[stage],
            "createdAt": now,
            "updatedAt": now,
        }
    )
    _write_yaml(target / "project.yaml", project)

    (target / "public" / "README.md").write_text(
        f"# {title.strip()}\n\n公開可能なログライン、人数、時間、注意事項だけを記録する。真相や秘密は書かない。\n",
        encoding="utf-8",
    )
    (target / "revisions" / "CHANGELOG.md").write_text(
        f"# {title.strip()} 変更履歴\n\n## Unreleased\n\n- 人間の原初メモから起票。\n",
        encoding="utf-8",
    )
    return target


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a human-led original murder-mystery workspace")
    parser.add_argument("slug")
    parser.add_argument("title")
    parser.add_argument("stage", nargs="?", default="00-inbox", choices=sorted(ALLOWED_STAGES))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    target = create_project(ROOT, args.slug, args.title, args.stage)
    print(target.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
