#!/usr/bin/env python3
"""Save recent workflow/task artifacts to a Google Drive folder for live editing/storage."""

from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

WORKFLOW_PATTERNS = [
    "README.md",
    "request.json",
    "output/package_edit_pass.md",
]

TASK_PATTERNS = [
    "notes/checklist.md",
    "notes/research.md",
    "materials_pricing.csv",
]


@dataclass(frozen=True)
class Artifact:
    kind: str
    project_slug: str
    path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy the last N workflow/task files from projects/ into Google Drive."
    )
    parser.add_argument(
        "--root",
        default="projects",
        help="Projects root directory relative to the repo (default: projects)",
    )
    parser.add_argument(
        "--drive-dir",
        default="~/Google Drive/Focus AI Engine",
        help="Destination Google Drive directory (default: ~/Google Drive/Focus AI Engine)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Number of most-recent workflow files and task files to copy (default: 3)",
    )
    return parser.parse_args()


def _collect(root: Path, patterns: Iterable[str], kind: str) -> list[Artifact]:
    artifacts: list[Artifact] = []
    for project_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        for rel_pattern in patterns:
            source = project_dir / rel_pattern
            if source.exists() and source.is_file():
                artifacts.append(Artifact(kind=kind, project_slug=project_dir.name, path=source))
    artifacts.sort(key=lambda item: item.path.stat().st_mtime, reverse=True)
    return artifacts


def copy_recent_artifacts(projects_root: Path, drive_dir: Path, limit: int) -> list[Path]:
    workflows = _collect(projects_root, WORKFLOW_PATTERNS, "workflow")[:limit]
    tasks = _collect(projects_root, TASK_PATTERNS, "task")[:limit]

    selected = workflows + tasks
    if not selected:
        return []

    stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = drive_dir / f"focus_sync_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest_lines = [
        "# Focus AI Engine sync",
        "",
        f"Generated (UTC): {datetime.now(tz=timezone.utc).isoformat()}",
        f"Projects root: {projects_root}",
        "",
        "## Included artifacts",
    ]

    copied_paths: list[Path] = []
    for artifact in selected:
        destination = run_dir / artifact.kind / artifact.project_slug / artifact.path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(artifact.path, destination)
        copied_paths.append(destination)
        manifest_lines.append(f"- {artifact.kind}: {artifact.path}")

    (run_dir / "SYNC_MANIFEST.md").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    return copied_paths


def main() -> int:
    args = parse_args()
    projects_root = Path(args.root).expanduser().resolve()
    drive_dir = Path(args.drive_dir).expanduser().resolve()

    if not projects_root.exists() or not projects_root.is_dir():
        raise SystemExit(f"Projects root does not exist: {projects_root}")
    if args.limit <= 0:
        raise SystemExit("--limit must be greater than 0")

    copied = copy_recent_artifacts(projects_root, drive_dir, args.limit)
    if not copied:
        print("No workflow/task artifacts found to copy.")
        return 0

    print(f"Copied {len(copied)} files to {drive_dir}")
    for path in copied:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
