#!/usr/bin/env python3
"""Render bootstrap-repo GitHub collaboration assets into a target repository."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = SKILL_ROOT / "assets" / "github"
WORKFLOW_TOKEN = '"__MAIN_CI_WORKFLOW_NAME__"'
ASSETS = {
    "PULL_REQUEST_TEMPLATE.md": Path(".github/PULL_REQUEST_TEMPLATE.md"),
    "workflows/issue-finalize.yml": Path(".github/workflows/issue-finalize.yml"),
    "scripts/issue-finalize.js": Path(".github/scripts/issue-finalize.js"),
}


def rendered_assets(main_ci_workflow: str) -> dict[Path, str]:
    name = main_ci_workflow.strip()
    if not name or "\n" in name or "\r" in name:
        raise ValueError("main CI workflow name must be a non-empty single line")

    rendered: dict[Path, str] = {}
    for source_name, destination in ASSETS.items():
        text = (ASSET_ROOT / source_name).read_text(encoding="utf-8")
        if source_name == "workflows/issue-finalize.yml":
            if text.count(WORKFLOW_TOKEN) != 1:
                raise ValueError("issue-finalize workflow must contain exactly one workflow-name token")
            text = text.replace(WORKFLOW_TOKEN, json.dumps(name, ensure_ascii=False))
        rendered[destination] = text
    return rendered


def render(root: Path, main_ci_workflow: str, *, overwrite: bool, dry_run: bool) -> dict[str, object]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"target root is not a directory: {root}")
    outputs = rendered_assets(main_ci_workflow)
    conflicts = [str(path) for path, content in outputs.items() if (root / path).exists() and (root / path).read_text(encoding="utf-8") != content]
    if conflicts and not overwrite and not dry_run:
        raise FileExistsError("refusing to overwrite different files without --overwrite: " + ", ".join(conflicts))

    if not dry_run:
        for relative, content in outputs.items():
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8", newline="\n")

    return {
        "root": str(root),
        "main_ci_workflow": main_ci_workflow.strip(),
        "files": [str(path) for path in outputs],
        "conflicts": conflicts,
        "overwrite_enabled": overwrite,
        "dry_run": dry_run,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Target repository root")
    parser.add_argument("--main-ci-workflow", required=True, help="Exact display name from the main CI workflow's top-level name field")
    parser.add_argument("--overwrite", action="store_true", help="Replace different existing collaboration files after they have been reviewed")
    parser.add_argument("--dry-run", action="store_true", help="Report the render plan without writing files")
    args = parser.parse_args()

    try:
        result = render(Path(args.root), args.main_ci_workflow, overwrite=args.overwrite, dry_run=args.dry_run)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
