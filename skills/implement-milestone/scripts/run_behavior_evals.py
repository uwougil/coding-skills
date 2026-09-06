#!/usr/bin/env python3
"""Run isolated semantic decision evals for the implement-milestone Skill."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "decision",
        "implementation_scope",
        "excluded_scope",
        "test_plan",
        "architecture_classification",
        "progressive_disclosure",
        "agent_infrastructure",
        "questions",
        "rationale",
    ],
    "properties": {
        "decision": {"enum": ["proceed", "block"]},
        "implementation_scope": {"type": "array", "items": {"type": "string"}},
        "excluded_scope": {"type": "array", "items": {"type": "string"}},
        "test_plan": {
            "type": "array",
            "items": {
                "enum": [
                    "unit",
                    "integration",
                    "e2e",
                    "regression",
                    "fixtures",
                    "schema",
                    "docs-links",
                ]
            },
        },
        "architecture_classification": {
            "enum": [
                "aligned",
                "implementation_drift",
                "outdated_derived_docs",
                "edd_design_conflict",
            ]
        },
        "progressive_disclosure": {
            "type": "object",
            "additionalProperties": False,
            "required": ["required", "source", "destination", "semantic_change"],
            "properties": {
                "required": {"type": "boolean"},
                "source": {"type": "string"},
                "destination": {"type": "string"},
                "semantic_change": {"type": "boolean"},
            },
        },
        "agent_infrastructure": {
            "type": "object",
            "additionalProperties": False,
            "required": ["introduce", "reason"],
            "properties": {
                "introduce": {"type": "boolean"},
                "reason": {"type": "string"},
            },
        },
        "questions": {"type": "array", "items": {"type": "string"}},
        "rationale": {"type": "string"},
    },
}

REQUIRED_RESULT_KEYS = set(SCHEMA["required"])


def extract_candidates(*texts: str | bytes) -> list[dict[str, Any]]:
    """Extract JSON objects emitted by a run, including progress/status streams."""
    candidates: list[dict[str, Any]] = []
    for text in texts:
        if isinstance(text, bytes):
            text = text.decode("utf-8", errors="replace")
        for line in text.splitlines():
            candidate_text = line.strip()
            if not (candidate_text.startswith("{") and candidate_text.endswith("}")):
                continue
            try:
                candidate = json.loads(candidate_text)
            except json.JSONDecodeError:
                continue
            if isinstance(candidate, dict) and REQUIRED_RESULT_KEYS <= candidate.keys():
                candidates.append(candidate)
    return candidates


BASE_AGENTS = """# Repository instructions
Use Python 3 and unittest. Keep changes minimal. Never add network dependencies unless EDD permits them.
"""


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    prd: str
    edd: str
    milestone: str
    extra_files: dict[str, str]
    check: Callable[[dict[str, Any]], list[str]]


def _joined(values: list[str]) -> str:
    return " ".join(values).lower()


def _expect_contains(value: str, needles: tuple[str, ...], label: str) -> list[str]:
    return [] if any(needle in value for needle in needles) else [f"{label} lacks one of {needles}"]


def check_ordinary(result: dict[str, Any]) -> list[str]:
    errors = []
    if result["decision"] != "proceed":
        errors.append("ordinary feature should proceed")
    errors += _expect_contains(_joined(result["implementation_scope"]), ("health", "status"), "scope")
    if "unit" not in result["test_plan"]:
        errors.append("ordinary local behavior should select unit tests")
    if result["questions"]:
        errors.append("ordinary feature should not ask questions")
    return errors


def check_non_goal(result: dict[str, Any]) -> list[str]:
    errors = []
    if result["decision"] != "proceed":
        errors.append("non-goal case should still proceed")
    errors += _expect_contains(_joined(result["excluded_scope"]), ("avatar",), "excluded_scope")
    if "avatar" in _joined(result["implementation_scope"]):
        errors.append("avatar upload leaked into implementation scope")
    return errors


def check_conflict(result: dict[str, Any]) -> list[str]:
    errors = []
    if result["decision"] != "block":
        errors.append("EDD conflict should block")
    if result["architecture_classification"] != "edd_design_conflict":
        errors.append("network prohibition should be an EDD design conflict")
    if not result["questions"]:
        errors.append("material EDD conflict should identify a user decision")
    return errors


def check_integration(result: dict[str, Any]) -> list[str]:
    errors = []
    if result["decision"] != "proceed":
        errors.append("integration case should proceed")
    if "integration" not in result["test_plan"]:
        errors.append("real service/database boundary requires integration testing")
    return errors


def check_progressive(result: dict[str, Any]) -> list[str]:
    errors = []
    disclosure = result["progressive_disclosure"]
    if not disclosure["required"]:
        errors.append("complex shared protocol should trigger progressive disclosure")
    if disclosure["semantic_change"]:
        errors.append("structural extraction must not change semantics")
    destination = disclosure["destination"].replace("\\", "/").lower()
    if not destination.startswith("docs/interfaces/"):
        errors.append("protocol detail should move under docs/interfaces/")
    return errors


def check_future_guard(result: dict[str, Any]) -> list[str]:
    errors = []
    excluded = _joined(result["excluded_scope"])
    included = _joined(result["implementation_scope"])
    errors += _expect_contains(excluded, ("csv", "export"), "excluded_scope")
    if "csv" in included or "export" in included:
        errors.append("next Milestone CSV export leaked into current scope")
    return errors


CASES = [
    EvalCase(
        "ordinary_feature",
        """# PRD
The product exposes an in-process health status returning `{"status": "ok"}`.
""",
        """# EDD
`app/service.py` owns health behavior. It has no I/O and no dependency on adapters.
Local behavior is verified with unit tests in `tests/`.
""",
        """# M1 Health status
## Scope
- Add `health_status()` in `app/service.py`.
## Non-goals
- Metrics and network endpoints.
## Acceptance Criteria
- Returns exactly `{"status": "ok"}`.
- A focused automated test verifies the behavior.
""",
        {"app/service.py": "def existing():\n    return True\n", "tests/test_service.py": ""},
        check_ordinary,
    ),
    EvalCase(
        "explicit_non_goal",
        """# PRD
Users can view a profile nickname. Account-security work is outside the current release.
""",
        """# EDD
Profile presentation belongs in `app/profile_view.py`; binary storage is not part of this module.
""",
        """# M1 Profile nickname
## Scope
- Render the existing nickname in the profile view.
## Non-goals
- Avatar upload.
- Password reset.
## Acceptance Criteria
- Existing nicknames are escaped and displayed.
""",
        {"app/profile_view.py": "def render_profile(nickname):\n    return ''\n"},
        check_non_goal,
    ),
    EvalCase(
        "edd_conflict",
        """# PRD
The calculator works fully offline and sends no user inputs outside the process.
""",
        """# EDD
All calculations execute in `core/`. Network clients and externally managed secrets are forbidden.
""",
        """# M1 Remote calculation
## Scope
- Call `https://calculator.example` for every calculation.
- Add an API-key configuration value.
## Non-goals
- Local calculation.
## Acceptance Criteria
- Remote responses are returned to the caller.
""",
        {"core/calculator.py": "def add(a, b):\n    return a + b\n"},
        check_conflict,
    ),
    EvalCase(
        "integration_boundary",
        """# PRD
Imported orders persist and can be loaded after the service is recreated.
""",
        """# EDD
`orders/service.py` owns use-case orchestration. `orders/sqlite_repository.py` is the real persistence adapter. Repository behavior must be integration-tested against SQLite.
""",
        """# M1 Persist imported orders
## Scope
- Connect the order service to the SQLite repository for import and reload.
## Non-goals
- Remote database support.
## Acceptance Criteria
- An imported order is present after constructing a new service over the same database.
""",
        {
            "orders/service.py": "class OrderService:\n    pass\n",
            "orders/sqlite_repository.py": "class SQLiteRepository:\n    pass\n",
        },
        check_integration,
    ),
    EvalCase(
        "progressive_disclosure",
        """# PRD
Existing clients retain the documented request/retry behavior.
""",
        """# EDD
## Client protocol
This protocol is canonical here but is consumed independently by web, mobile, and worker modules.
It has its own versioning lifecycle and contains request envelopes, retry states, error mappings,
compatibility tables, idempotency rules, timeout rules, examples, and rollout constraints.
The current Milestone must preserve every one of these semantics while changing document topology only.

### Request envelope
Clients send an idempotency key and protocol version.

### Retry and errors
Only transient errors are retried; validation errors are final.

### Compatibility
Web, mobile, and worker support protocol version 2.
""",
        """# M1 Protocol maintenance
## Scope
- Update the existing retry implementation without changing protocol semantics.
- Apply content-preserving structural extraction when the EDD section qualifies.
## Non-goals
- Protocol version 3 or changed error semantics.
## Acceptance Criteria
- Existing retry semantics remain intact.
- Shared protocol detail has one canonical location and EDD retains a summary and link.
""",
        {
            "web/client.py": "# consumes protocol v2\n",
            "mobile/client.py": "# consumes protocol v2\n",
            "worker/client.py": "# consumes protocol v2\n",
        },
        check_progressive,
    ),
    EvalCase(
        "future_milestone_guard",
        """# PRD
Invoices calculate totals. CSV export is a later release capability.
""",
        """# EDD
`billing/invoice.py` owns calculations. Export adapters may consume invoice results but must not be introduced before their Milestone.
""",
        """# M1 Invoice totals
## Scope
- Implement subtotal and tax calculation.
## Non-goals
- CSV export, which belongs to M2.
## Acceptance Criteria
- Total equals subtotal plus configured tax.
""",
        {
            "billing/invoice.py": "# totals are not implemented yet\n# CSV export is planned for M2\n",
            "docs/milestones/m2.md": "# M2\n## Scope\n- Add CSV export.\n",
        },
        check_future_guard,
    ),
]


PROMPT = """Use $implement-milestone for a non-mutating behavioral evaluation of docs/milestones/m1.md.
Read every required source and relevant code/test context. Do not edit files and do not run state-changing commands.
This is a pre-implementation decision test: after reading enough evidence, STOP and return exactly one final JSON object using the required schema. Do not narrate progress, emit interim JSON, or continue inspecting after the final decision.
`implementation_scope` must list only current-Milestone work; `excluded_scope` must name relevant Non-goals and later work.
Select every justified test layer. Use empty strings for progressive-disclosure source/destination when not required.
For a material conflict, set `decision` to `block`, set `architecture_classification` to `edd_design_conflict` when EDD semantics conflict, and put one concise decision question in `questions`.
Set `questions` empty only when no user decision is needed.
"""


def write_repo(root: Path, case: EvalCase) -> None:
    files = {
        "AGENTS.md": BASE_AGENTS,
        "docs/PRD.md": case.prd,
        "docs/EDD.md": case.edd,
        "docs/milestones/m1.md": case.milestone,
        **case.extra_files,
    }
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "init", "--quiet"], cwd=root, check=True)


def run_case(case: EvalCase, codex: str, timeout: int) -> dict[str, Any]:
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix=f"implement-milestone-{case.case_id}-") as directory:
        root = Path(directory)
        write_repo(root, case)
        schema_path = root / "eval-schema.json"
        output_path = root / "eval-output.json"
        schema_path.write_text(json.dumps(SCHEMA), encoding="utf-8")
        command = [
            codex,
            "exec",
            "--ephemeral",
            "--model",
            "gpt-5.6-luna",
            "-c",
            'model_reasoning_effort="low"',
            "--sandbox",
            "read-only",
            "--cd",
            str(root),
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(output_path),
            PROMPT,
        ]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            partial_stdout = exc.stdout or ""
            partial_stderr = exc.stderr or ""
            candidates = extract_candidates(partial_stdout, partial_stderr)
            if candidates:
                result = candidates[-1]
                errors = case.check(result)
                return {
                    "id": case.case_id,
                    "passed": not errors,
                    "duration_seconds": round(time.monotonic() - started, 2),
                    "errors": errors + ["codex continued past timeout after emitting a decision"],
                    "decision": result,
                }
            return {
                "id": case.case_id,
                "passed": False,
                "duration_seconds": round(time.monotonic() - started, 2),
                "errors": [f"codex timed out after {timeout}s"],
                "stdout": exc.stdout or "",
                "stderr": exc.stderr or "",
            }

        if completed.returncode != 0:
            candidates = extract_candidates(completed.stdout, completed.stderr)
            if candidates:
                result = candidates[-1]
                errors = case.check(result)
                return {
                    "id": case.case_id,
                    "passed": not errors,
                    "duration_seconds": round(time.monotonic() - started, 2),
                    "errors": errors + [f"codex exited with {completed.returncode} after emitting a decision"],
                    "decision": result,
                }
            return {
                "id": case.case_id,
                "passed": False,
                "duration_seconds": round(time.monotonic() - started, 2),
                "errors": [f"codex exited with {completed.returncode}"],
                "stdout": completed.stdout[-4000:],
                "stderr": completed.stderr[-4000:],
            }
        try:
            result = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return {
                "id": case.case_id,
                "passed": False,
                "duration_seconds": round(time.monotonic() - started, 2),
                "errors": [f"invalid structured output: {exc}"],
                "stdout": completed.stdout[-4000:],
                "stderr": completed.stderr[-4000:],
            }

        errors = case.check(result)
        return {
            "id": case.case_id,
            "passed": not errors,
            "duration_seconds": round(time.monotonic() - started, 2),
            "errors": errors,
            "decision": result,
        }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case",
        action="append",
        choices=[case.case_id for case in CASES],
        help="Run only this case; repeat to select multiple cases",
    )
    parser.add_argument("--timeout", type=int, default=240, help="Seconds per case")
    parser.add_argument("--json", action="store_true", help="Emit full JSON results")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    codex = shutil.which("codex")
    if not codex:
        print("error: codex CLI is not available", file=sys.stderr)
        return 2
    if not shutil.which("git"):
        print("error: git is not available", file=sys.stderr)
        return 2

    selected = [case for case in CASES if not args.case or case.case_id in args.case]
    results = []
    for case in selected:
        result = run_case(case, codex, args.timeout)
        results.append(result)
        if not args.json:
            marker = "PASS" if result["passed"] else "FAIL"
            print(f"{marker} {result['id']} ({result['duration_seconds']}s)", flush=True)
            for error in result["errors"]:
                print(f"  - {error}", flush=True)
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"{sum(item['passed'] for item in results)}/{len(results)} passed")
    return 0 if all(result["passed"] for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
