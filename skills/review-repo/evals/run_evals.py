#!/usr/bin/env python3
"""Run behavioral review-repo evals through isolated Codex CLI sessions."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys


HERE = Path(__file__).resolve().parent
WORK = HERE / "_work"
RESULTS = HERE / "results"
SCHEMA = HERE / "output-schema.json"
CASES_FILE = HERE / "cases.json"
SKILL_ROOT = HERE.parent
PROMPT = """Use $review-repo to perform a full semantic audit of this entire repository.
This is an isolated evaluation fixture. Stay read-only and do not modify any file. Read the applicable
AGENTS.md, docs/PRD.md, docs/EDD.md, repository-visible Issue and PR artifacts, source, tests, and derived docs.
Apply the skill's finding threshold: report material evidence-backed issues and do not invent style
findings. Return only the JSON required by the supplied output schema. In each evidence string include
a repository-relative path and a tight line range, symbol, test, or command result.
Copy path names exactly, including leading dots in hidden directories such as `.github/`.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=3, help="maximum concurrent Codex sessions")
    parser.add_argument("--case", action="append", dest="cases", help="run only this case ID; repeatable")
    parser.add_argument("--model", help="optional explicit Codex model override")
    parser.add_argument("--rebuild", action="store_true", help="rebuild fixtures before running")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_evidence(value: str) -> str:
    """Normalize slash style and optional-dot rendering for GitHub metadata paths."""
    return value.replace("\\", "/").lower().replace(".github/", "github/")


def ensure_fixtures(rebuild: bool) -> None:
    if rebuild or not WORK.is_dir():
        subprocess.run([sys.executable, str(HERE / "build_fixtures.py")], check=True)


def run_case(codex: str, case: dict, model: str | None) -> dict:
    case_id = case["id"]
    root = WORK / case_id
    output = RESULTS / f"{case_id}.json"
    log = RESULTS / f"{case_id}.log"
    command = [
        codex, "exec", "--ephemeral", "--sandbox", "read-only", "--skip-git-repo-check",
        "--cd", str(root), "--add-dir", str(SKILL_ROOT),
        "--output-schema", str(SCHEMA), "--output-last-message", str(output),
    ]
    if model:
        command.extend(["--model", model])
    command.append(
        PROMPT
        + f"\nRead and follow the current skill under evaluation at {SKILL_ROOT / 'SKILL.md'} "
        "and its linked references; it overrides any older installed copy.\n"
    )
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log.write_text(completed.stdout + "\n--- STDERR ---\n" + completed.stderr, encoding="utf-8")

    status = subprocess.run(
        ["git", "-C", str(root), "status", "--short"], capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False,
    ).stdout.strip()
    errors: list[str] = []
    combined_output = f"{completed.stdout}\n{completed.stderr}".lower()
    blocked = any(
        marker in combined_output
        for marker in ("you've hit your usage limit", "usage limit", "rate limit", "quota exceeded")
    )
    block_reason = "Codex service quota/usage limit prevented an independent run." if blocked else None
    report: dict | None = None
    if completed.returncode != 0:
        if not blocked:
            errors.append(f"codex exited {completed.returncode}")
    if not output.exists():
        if not blocked:
            errors.append("no final output file")
    else:
        try:
            report = load_json(output)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON output: {exc}")
    if status:
        errors.append(f"review changed worktree: {status}")

    if report is not None:
        findings = report.get("findings", [])
        for required in case.get("required_findings", []):
            match = None
            for finding in findings:
                evidence = normalize_evidence("\n".join(finding.get("evidence", [])))
                if finding.get("category") not in required["category_any"]:
                    continue
                if all(normalize_evidence(path) in evidence for path in required["evidence_all"]):
                    match = finding
                    break
            if match is None:
                errors.append(
                    "missing finding with category in "
                    f"{required['category_any']} and evidence {required['evidence_all']}"
                )
        maximum = case.get("max_findings")
        if maximum is not None and len(findings) > maximum:
            errors.append(f"expected at most {maximum} findings, got {len(findings)}")
        report_evidence = normalize_evidence(
            "\n".join(
                evidence
                for finding in findings
                for evidence in finding.get("evidence", [])
            )
        )
        missing_report_evidence = [
            path for path in case.get("required_report_evidence_all", [])
            if normalize_evidence(path) not in report_evidence
        ]
        if missing_report_evidence:
            errors.append(f"missing report-level evidence {missing_report_evidence}")
        categories = {finding.get("category") for finding in findings}
        missing_categories = [
            category for category in case.get("required_categories_all", [])
            if category not in categories
        ]
        if missing_categories:
            errors.append(f"missing report categories {missing_categories}")
        expected_candidate = case.get("candidate")
        if expected_candidate is not None:
            candidates = report.get("issue_candidates", [])
            if not any(candidate.get("eligible") is expected_candidate["eligible"] for candidate in candidates):
                errors.append(f"missing issue candidate with eligible={expected_candidate['eligible']}")

    return {
        "id": case_id,
        "scenario": case["scenario"],
        "passed": not errors and not blocked,
        "blocked": blocked,
        "block_reason": block_reason,
        "errors": errors,
        "report": report,
        "output": str(output),
        "log": str(log),
    }


def write_summary(results: list[dict], codex_version: str) -> None:
    passed = sum(result["passed"] for result in results)
    blocked = sum(result.get("blocked", False) for result in results)
    failed = len(results) - passed - blocked
    lines = [
        "# review-repo behavioral eval results",
        "",
        f"- Run (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"- Codex CLI: `{codex_version}`",
        f"- Result: **{passed}/{len(results)} passed; {failed} failed; {blocked} blocked**",
        "- Method: each fixture was reviewed in a separate ephemeral, read-only Codex session using `$review-repo`; structured results were graded on semantic category plus evidence paths, not prose wording.",
        "- False-positive gates: the healthy repository must return zero findings, and semantic ambiguity must not become an auto-eligible Issue candidate.",
        "",
        "| Case | Result | Findings | Notes |",
        "| --- | --- | ---: | --- |",
    ]
    for result in results:
        report = result["report"] or {}
        count = len(report.get("findings", []))
        notes = "; ".join(result["errors"]) if result["errors"] else "Required semantic signal and evidence found"
        status = "PASS" if result["passed"] else ("BLOCKED" if result.get("blocked") else "FAIL")
        if result.get("blocked"):
            notes = result.get("block_reason", "Independent run unavailable")
        lines.append(f"| `{result['id']}` | {status} | {count} | {notes} |")
    lines.extend([
        "",
        "## What this eval establishes",
        "",
        "The cases exercise PRD conflict, EDD dependency drift, closed-Issue acceptance gaps, missing PR provenance, cross-PR architecture drift, stale derived documentation, semantic ambiguity, unnecessary agent infrastructure, and a healthy repository. A passing result shows that the skill produced the expected evidence-bearing category, applied the review-to-Issue eligibility guard, and preserved the worktree.",
        "",
        "## Limits of this eval",
        "",
        "These fixtures are intentionally small and synthetic. Results can vary across models, reasoning settings, and future Codex releases. A BLOCKED case means the independent Codex session could not run (for example, service quota); it is neither a pass nor a skill failure. Path/category grading checks review decisions and evidence linkage, but it does not prove severity calibration on large polyglot repositories, generated code at scale, partial checkouts, or unavailable external CI/runtime dependencies. Re-run blocked cases when the service is available and rerun after material skill or model changes.",
        "",
    ])
    (HERE / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    if args.jobs < 1:
        raise SystemExit("--jobs must be positive")
    codex = shutil.which("codex")
    if not codex:
        raise SystemExit("codex executable not found")
    ensure_fixtures(args.rebuild)
    RESULTS.mkdir(exist_ok=True)

    manifest = load_json(CASES_FILE)["cases"]
    selected = set(args.cases or [])
    cases = [case for case in manifest if not selected or case["id"] in selected]
    missing = selected - {case["id"] for case in cases}
    if missing:
        raise SystemExit(f"unknown case IDs: {', '.join(sorted(missing))}")
    if not cases:
        raise SystemExit("no eval cases selected")

    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=min(args.jobs, len(cases))) as pool:
        futures = {pool.submit(run_case, codex, case, args.model): case["id"] for case in cases}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            status = "PASS" if result["passed"] else ("BLOCKED" if result.get("blocked") else "FAIL")
            print(f"{status} {result['id']}", flush=True)
            for error in result["errors"]:
                print(f"  {error}")

    order = {case["id"]: index for index, case in enumerate(cases)}
    results.sort(key=lambda result: order[result["id"]])
    version = subprocess.run([codex, "--version"], capture_output=True, text=True, check=False).stdout.strip()
    write_summary(results, version)
    if any(not result["passed"] and not result.get("blocked") for result in results):
        return 1
    if any(result.get("blocked") for result in results):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
