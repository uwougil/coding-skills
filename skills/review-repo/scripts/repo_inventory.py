#!/usr/bin/env python3
"""Produce a bounded, read-only inventory for progressive repository review."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Iterable


SKIP_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode", "node_modules", "vendor",
    "dist", "build", "target", "coverage", ".next", ".nuxt", ".cache",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "__pycache__", ".venv", "venv",
}
BINARY_SUFFIXES = {
    ".7z", ".a", ".avi", ".bin", ".bmp", ".class", ".dll", ".dylib", ".exe",
    ".gif", ".gz", ".ico", ".jar", ".jpeg", ".jpg", ".mov", ".mp3", ".mp4",
    ".o", ".obj", ".pdf", ".png", ".pyc", ".so", ".tar", ".webp", ".woff",
    ".woff2", ".zip",
}
SOURCE_SUFFIXES = {
    ".c", ".cc", ".cpp", ".cs", ".ex", ".exs", ".go", ".h", ".hpp", ".java",
    ".js", ".jsx", ".kt", ".kts", ".m", ".mm", ".php", ".py", ".rb", ".rs",
    ".scala", ".sh", ".swift", ".ts", ".tsx", ".vue",
}
MANIFEST_NAMES = {
    "build.gradle", "build.gradle.kts", "cargo.toml", "composer.json", "gemfile",
    "go.mod", "makefile", "package.json", "pom.xml", "pyproject.toml", "requirements.txt",
}


def git(root: Path, *args: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=8, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False, ""
    return result.returncode == 0, result.stdout.strip()


def walk(root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not Path(current, d).is_symlink())
        for name in sorted(files):
            path = Path(current, name)
            if not path.is_symlink():
                yield path


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_test(path: str) -> bool:
    lower = path.lower()
    name = Path(lower).name
    return (
        lower.startswith(("test/", "tests/", "spec/", "specs/", "e2e/"))
        or "/test/" in lower or "/tests/" in lower or "/__tests__/" in lower
        or name.startswith("test_") or name.endswith(("_test.py", ".test.js", ".test.ts", ".spec.js", ".spec.ts"))
    )


def categorize(path: str) -> set[str]:
    p = Path(path)
    lower = path.lower()
    name = p.name.lower()
    suffix = p.suffix.lower()
    categories: set[str] = set()

    if lower in {"docs/prd.md", "prd.md"} or name.startswith("prd."):
        categories.add("prd")
    if lower in {"docs/edd.md", "edd.md"} or name.startswith("edd."):
        categories.add("edd")
    if "milestone" in lower and suffix in {".md", ".txt", ".yaml", ".yml"}:
        categories.add("milestones")
    if name in {"agents.md", "agents.override.md"}:
        categories.add("agent_instructions")
    if lower.startswith(".agents/skills/") or lower.startswith(".codex/agents/"):
        categories.add("agent_infrastructure")
    if name in {".mcp.json", "mcp.json", "plugin.json"} or "mcp" in lower or ".codex-plugin/" in lower:
        categories.add("agent_infrastructure")
    if lower.startswith((".github/workflows/", ".gitlab/")) or name in {
        ".gitlab-ci.yml", "azure-pipelines.yml", "buildkite.yml", "jenkinsfile"
    }:
        categories.add("ci")
    if is_test(path):
        categories.add("tests")
    elif suffix in SOURCE_SUFFIXES:
        categories.add("source")
    if name in MANIFEST_NAMES or name.endswith((".csproj", ".sln")):
        categories.add("manifests")
    if name.startswith("readme") or name in {".env.example", "docker-compose.yml", "docker-compose.yaml"}:
        categories.add("derived_docs")
    if lower.startswith(("docs/generated/", "generated/")) or name in {
        "openapi.json", "openapi.yaml", "openapi.yml", "schema.json"
    }:
        categories.add("generated")
    if suffix in {".md", ".mdx", ".rst"}:
        categories.add("docs")
    if any(token in lower for token in ("structural", "design-change", "architecture-change", "doc-migration")):
        categories.add("structural_logs")
    return categories


def inventory(root: Path, max_paths: int) -> dict:
    buckets: dict[str, list[str]] = {
        key: [] for key in (
            "prd", "edd", "milestones", "agent_instructions", "agent_infrastructure",
            "manifests", "source", "tests", "ci", "docs", "derived_docs", "generated",
            "structural_logs", "large_text_files",
        )
    }
    counts = {key: 0 for key in buckets}
    total_files = 0
    total_bytes = 0

    for path in walk(root):
        total_files += 1
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        total_bytes += size
        path_rel = rel(path, root)
        cats = categorize(path_rel)
        if size >= 500_000 and path.suffix.lower() not in BINARY_SUFFIXES:
            cats.add("large_text_files")
        for category in cats:
            counts[category] += 1
            if len(buckets[category]) < max_paths:
                buckets[category].append(path_rel)

    is_repo, top = git(root, "rev-parse", "--show-toplevel")
    branch_ok, branch = git(root, "branch", "--show-current")
    head_ok, head = git(root, "rev-parse", "--short", "HEAD")
    status_ok, status = git(root, "status", "--short")
    log_ok, recent = git(root, "log", "-n", "10", "--date=short", "--pretty=format:%h %ad %s")

    return {
        "schema_version": 1,
        "root": str(root),
        "totals": {"files": total_files, "bytes": total_bytes},
        "git": {
            "is_repository": is_repo,
            "top_level": top if is_repo else None,
            "branch": branch if branch_ok and branch else None,
            "head": head if head_ok else None,
            "status": status.splitlines() if status_ok and status else [],
            "recent_commits": recent.splitlines() if log_ok and recent else [],
        },
        "category_counts": counts,
        "paths": buckets,
        "notes": [
            f"Path lists are capped at {max_paths} entries per category.",
            "Generated and dependency directories are intentionally skipped.",
            "Categories are discovery hints, not review conclusions.",
        ],
    }


def as_markdown(data: dict) -> str:
    lines = [
        "# Repository inventory",
        "",
        f"- Root: `{data['root']}`",
        f"- Files scanned: {data['totals']['files']}",
        f"- Bytes represented: {data['totals']['bytes']}",
        f"- Git repository: {str(data['git']['is_repository']).lower()}",
        f"- Branch: `{data['git']['branch'] or 'unknown'}`",
        f"- HEAD: `{data['git']['head'] or 'unknown'}`",
    ]
    if data["git"]["status"]:
        lines.extend(["", "## Worktree status", "", "```text", *data["git"]["status"], "```"])
    for category, paths in data["paths"].items():
        count = data["category_counts"][category]
        if not count:
            continue
        lines.extend(["", f"## {category.replace('_', ' ').title()} ({count})", ""])
        lines.extend(f"- `{path}`" for path in paths)
        if count > len(paths):
            lines.append(f"- ... {count - len(paths)} more")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root or directory to inspect")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--max-paths-per-category", type=int, default=80)
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")
    if args.max_paths_per_category < 1:
        parser.error("--max-paths-per-category must be positive")

    data = inventory(root, args.max_paths_per_category)
    if args.format == "markdown":
        sys.stdout.write(as_markdown(data))
    else:
        json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
