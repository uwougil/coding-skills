#!/usr/bin/env python3
"""Validate the portable skill repository package."""

from __future__ import annotations

import json
import ast
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
EXPECTED_SKILLS = {
    "bootstrap-repo",
    "implement-milestone",
    "fix-bug",
    "review-repo",
    "create-issue",
}
REQUIRED_UI_KEYS = ("display_name", "short_description", "default_prompt")
LOCAL_PATH_RE = re.compile(r"(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]|/(?:Users|home)/)")


def frontmatter(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) < 4 or lines[0].strip() != "---":
        raise ValueError(f"{path}: missing YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"{path}: unterminated YAML frontmatter") from exc
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.match(r"^(name|description):\s*(.+?)\s*$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip('"\'')
    for key in ("name", "description"):
        if not fields.get(key):
            raise ValueError(f"{path}: frontmatter field {key!r} is empty or missing")
    return fields["name"], fields["description"]


def validate() -> list[str]:
    errors: list[str] = []
    actual = {
        path.name for path in SKILLS_DIR.iterdir() if path.is_dir()
    } if SKILLS_DIR.is_dir() else set()
    if actual != EXPECTED_SKILLS:
        errors.append(f"skills directory must contain exactly {sorted(EXPECTED_SKILLS)}; found {sorted(actual)}")

    for name in sorted(EXPECTED_SKILLS):
        skill_root = SKILLS_DIR / name
        entrypoint = skill_root / "SKILL.md"
        ui = skill_root / "agents" / "openai.yaml"
        if not entrypoint.is_file():
            errors.append(f"{name}: missing SKILL.md")
            continue
        try:
            declared_name, _ = frontmatter(entrypoint)
            if declared_name != name:
                errors.append(f"{entrypoint}: frontmatter name is {declared_name!r}, expected {name!r}")
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(str(exc))
        if not ui.is_file():
            errors.append(f"{name}: missing agents/openai.yaml")
        else:
            ui_text = ui.read_text(encoding="utf-8")
            for key in REQUIRED_UI_KEYS:
                if not re.search(rf"^\s*{re.escape(key)}:\s*\S", ui_text, re.MULTILINE):
                    errors.append(f"{ui}: missing interface field {key!r}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {".git", "__pycache__", "_work"} for part in path.parts):
            continue
        if path.suffix in {".pyc", ".log"}:
            errors.append(f"generated file must not be packaged: {path.relative_to(ROOT)}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError as exc:
            errors.append(f"{path.relative_to(ROOT)} is not UTF-8: {exc}")
            continue
        if path.suffix == ".py":
            try:
                ast.parse(text, filename=str(path))
            except SyntaxError as exc:
                errors.append(f"invalid Python in {path.relative_to(ROOT)}: {exc}")
        if LOCAL_PATH_RE.search(text) and path.name not in {"validate_skills.py"}:
            errors.append(f"machine-local path found in {path.relative_to(ROOT)}")
        if path.suffix == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                errors.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Skill package validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(EXPECTED_SKILLS)} skill packages and their UTF-8/JSON assets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
