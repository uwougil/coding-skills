#!/usr/bin/env python3
"""Read-only repository probe for bootstrap-repo.

Prints a JSON snapshot of intent files, implementation markers, Git state,
agent infrastructure, and suspicious tracked filenames. It performs no writes,
network requests, authentication checks, or dependency installation.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "target",
    "coverage",
    "__pycache__",
}

STACK_MARKERS = {
    "python": ["pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "uv.lock", "poetry.lock"],
    "node": ["package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb"],
    "rust": ["Cargo.toml", "Cargo.lock"],
    "go": ["go.mod", "go.sum"],
    "java": ["pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"],
    "dotnet": ["global.json", "Directory.Build.props"],
    "ruby": ["Gemfile", "gems.rb"],
    "php": ["composer.json", "composer.lock"],
}

SUSPICIOUS_TRACKED = [
    re.compile(r"(^|/)\.env($|\.)", re.IGNORECASE),
    re.compile(r"(^|/)(id_rsa|id_ed25519|credentials)(\.|$)", re.IGNORECASE),
    re.compile(r"\.(pem|p12|pfx|key)$", re.IGNORECASE),
    re.compile(r"(^|/)(secrets?|tokens?)(\.|/|$)", re.IGNORECASE),
]


def run(command: list[str], root: Path, timeout: int = 8) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "exit_code": None, "stdout": "", "error": type(exc).__name__}
    return {
        "ok": completed.returncode == 0,
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "error": completed.stderr.strip()[:500],
    }


def relative_files(root: Path, limit: int = 10000) -> list[str]:
    found: list[str] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            path = Path(current, name)
            try:
                found.append(path.relative_to(root).as_posix())
            except ValueError:
                continue
            if len(found) >= limit:
                return found
    return found


def redact_remote(value: str) -> str:
    # Preserve repository identity while removing URL userinfo if present.
    return re.sub(r"(?i)(https?://)[^/@\s]+@", r"\1<redacted>@", value)


def git_snapshot(root: Path) -> dict[str, Any]:
    if not shutil.which("git"):
        return {"available": False, "inside_work_tree": False}

    inside = run(["git", "rev-parse", "--is-inside-work-tree"], root)
    is_repo = inside["ok"] and inside["stdout"] == "true"
    snapshot: dict[str, Any] = {"available": True, "inside_work_tree": is_repo}
    if not is_repo:
        return snapshot

    branch = run(["git", "branch", "--show-current"], root)
    status = run(["git", "status", "--short"], root)
    history = run(["git", "rev-parse", "--verify", "HEAD"], root)
    remotes = run(["git", "remote", "-v"], root)
    tracked = run(["git", "ls-files"], root)

    tracked_files = tracked["stdout"].splitlines() if tracked["ok"] else []
    suspicious = sorted(
        path
        for path in tracked_files
        if Path(path).name.lower() not in {".env.example", ".env.sample"}
        and any(pattern.search(path) for pattern in SUSPICIOUS_TRACKED)
    )
    snapshot.update(
        {
            "has_commits": history["ok"],
            "head": history["stdout"] if history["ok"] else None,
            "branch": branch["stdout"] if branch["ok"] else None,
            "status_short": status["stdout"].splitlines() if status["stdout"] else [],
            "remotes": [redact_remote(line) for line in remotes["stdout"].splitlines()] if remotes["ok"] else [],
            "suspicious_tracked_paths": suspicious,
        }
    )
    return snapshot


def build_snapshot(root: Path) -> dict[str, Any]:
    files = relative_files(root)
    file_set = set(files)
    canonical = {
        "prd": "docs/PRD.md" in file_set,
        "edd": "docs/EDD.md" in file_set,
    }
    draft_candidates = sorted(
        path
        for path in files
        if path.lower().endswith(".md")
        and any(term in Path(path).stem.lower() for term in ("prd", "edd", "requirements", "design"))
        and path not in {"docs/PRD.md", "docs/EDD.md"}
    )
    stacks = {
        stack: [marker for marker in markers if marker in file_set]
        for stack, markers in STACK_MARKERS.items()
        if any(marker in file_set for marker in markers)
    }
    source_files = [
        path
        for path in files
        if path.startswith(("src/", "app/", "lib/", "packages/", "cmd/"))
    ]
    workflows = sorted(path for path in files if path.startswith(".github/workflows/") and path.lower().endswith((".yml", ".yaml")))
    git = git_snapshot(root)
    # A lone package manifest is often part of an unfinished bootstrap. History,
    # implementation, or CI is stronger evidence that evolution mode is safer.
    meaningful = bool(git.get("has_commits") or source_files or workflows)

    return {
        "root": str(root),
        "suggested_mode": "existing-re-bootstrap" if meaningful else "new-bootstrap",
        "intent": {**canonical, "draft_candidates": draft_candidates},
        "stack_markers": stacks,
        "source_file_count": len(source_files),
        "ci_workflows": workflows,
        "delivery_contract": {
            "pull_request_template": any(
                path.lower() in {
                    ".github/pull_request_template.md",
                    "pull_request_template.md",
                    "docs/pull_request_template.md",
                }
                or path.lower().startswith(".github/pull_request_template/")
                for path in files
            ),
            "issue_templates": sorted(
                path for path in files if path.lower().startswith(".github/issue_template/")
            ),
        },
        "agent_infrastructure": {
            "agents_md": "AGENTS.md" in file_set,
            "project_skills": sorted(path for path in files if path.startswith(".agents/skills/") and path.endswith("/SKILL.md")),
            "project_mcp_config": ".codex/config.toml" in file_set,
            "plugin_manifest": ".codex-plugin/plugin.json" in file_set,
        },
        "tools": {name: shutil.which(name) for name in ("git", "gh")},
        "git": git,
        "scan_truncated": len(files) >= 10000,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a repository without modifying it.")
    parser.add_argument("--root", default=".", help="Repository or project directory")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")
    # ASCII escapes keep paths unambiguous on Windows consoles with legacy code pages.
    print(json.dumps(build_snapshot(root), ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
