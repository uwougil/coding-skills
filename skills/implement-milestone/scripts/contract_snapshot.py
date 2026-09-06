#!/usr/bin/env python3
"""Read-only preflight for an implement-milestone execution contract.

This helper verifies canonical file locations and prints metadata and fingerprints.
It intentionally does not summarize or interpret the documents; the agent must read
the originals and make semantic scope/architecture decisions itself.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
SECTION_ALIASES = {
    "scope": {"scope", "in scope", "deliverables"},
    "non_goals": {"non-goals", "non goals", "non-goal", "out of scope"},
    "acceptance_criteria": {
        "acceptance criteria",
        "acceptance criterion",
        "completion criteria",
        "done criteria",
    },
}


def _git_root(cwd: Path) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    value = result.stdout.strip()
    return Path(value).resolve() if value else None


def resolve_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    cwd = Path.cwd().resolve()
    return _git_root(cwd) or cwd


def _is_within(path: Path, directory: Path) -> bool:
    try:
        return os.path.commonpath(
            [os.path.normcase(str(path)), os.path.normcase(str(directory))]
        ) == os.path.normcase(str(directory))
    except ValueError:
        return False


def resolve_milestone(root: Path, value: str) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve()
    milestone_dir = (root / "docs" / "milestones").resolve()
    if not _is_within(candidate, milestone_dir):
        raise ValueError(
            f"Milestone must be inside {milestone_dir}; received {candidate}"
        )
    return candidate


def _headings(text: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = HEADING_RE.match(line)
        if match:
            result.append(
                {
                    "level": len(match.group(1)),
                    "title": match.group(2).strip(),
                    "line": line_number,
                }
            )
    return result


def inspect_file(path: Path, root: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    try:
        display_path = path.relative_to(root).as_posix()
    except ValueError:
        display_path = str(path)
    return {
        "path": display_path,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "lines": len(text.splitlines()),
        "headings": _headings(text),
    }


def build_snapshot(root: Path, milestone: Path) -> tuple[dict[str, Any], int]:
    required = [
        root / "AGENTS.md",
        root / "docs" / "PRD.md",
        root / "docs" / "EDD.md",
        milestone,
    ]
    missing = []
    unreadable = []
    files: list[dict[str, Any]] = []
    for path in required:
        if not path.is_file():
            missing.append(str(path))
            continue
        try:
            files.append(inspect_file(path, root))
        except (OSError, UnicodeError) as exc:
            unreadable.append({"path": str(path), "error": str(exc)})

    warnings: list[str] = []
    milestone_relative = milestone.relative_to(root).as_posix()
    milestone_record = next(
        (item for item in files if item["path"] == milestone_relative),
        None,
    )
    recognized: dict[str, bool] = {key: False for key in SECTION_ALIASES}
    if milestone_record:
        normalized_headings = {
            re.sub(r"\s+", " ", item["title"].strip().lower())
            for item in milestone_record["headings"]
        }
        for key, aliases in SECTION_ALIASES.items():
            recognized[key] = bool(normalized_headings & aliases)
            if not recognized[key]:
                warnings.append(
                    f"Milestone has no recognized {key.replace('_', ' ')} heading; "
                    "inspect the original content rather than assuming it is absent."
                )

    payload: dict[str, Any] = {
        "status": "ok" if not missing and not unreadable else "error",
        "repository_root": str(root),
        "authority_order": ["PRD", "EDD", "Milestone", "Implementation"],
        "files": files,
        "milestone_sections_recognized": recognized,
        "missing": missing,
        "unreadable": unreadable,
        "warnings": warnings,
        "notice": (
            "Metadata only: read and interpret every original source before planning or editing."
        ),
    }
    return payload, 0 if payload["status"] == "ok" else 2


def _render_text(payload: dict[str, Any]) -> str:
    lines = [
        f"status: {payload['status']}",
        f"repository_root: {payload['repository_root']}",
        "authority_order: PRD -> EDD -> Milestone -> Implementation",
    ]
    for item in payload["files"]:
        lines.append(
            f"file: {item['path']} lines={item['lines']} sha256={item['sha256']}"
        )
    for value in payload["missing"]:
        lines.append(f"missing: {value}")
    for item in payload["unreadable"]:
        lines.append(f"unreadable: {item['path']}: {item['error']}")
    for warning in payload["warnings"]:
        lines.append(f"warning: {warning}")
    lines.append(payload["notice"])
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify and fingerprint implement-milestone contract sources."
    )
    parser.add_argument("--repo-root", help="Repository root; defaults to Git root or CWD")
    parser.add_argument(
        "--milestone",
        required=True,
        help="Milestone path, which must resolve under docs/milestones/",
    )
    parser.add_argument(
        "--format", choices=("text", "json"), default="text", help="Output format"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = resolve_root(args.repo_root)
    try:
        milestone = resolve_milestone(root, args.milestone)
        payload, exit_code = build_snapshot(root, milestone)
    except ValueError as exc:
        payload = {
            "status": "error",
            "repository_root": str(root),
            "error": str(exc),
        }
        exit_code = 2

    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif "error" in payload and "files" not in payload:
        print(f"status: error\nrepository_root: {root}\nerror: {payload['error']}")
    else:
        print(_render_text(payload))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
