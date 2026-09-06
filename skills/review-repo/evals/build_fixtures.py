#!/usr/bin/env python3
"""Materialize small, deterministic repository fixtures for review-repo evals."""

from __future__ import annotations

from pathlib import Path
import os
import shutil
import stat
import subprocess
import textwrap


HERE = Path(__file__).resolve().parent
WORK = HERE / "_work"


COMMON = {
    ".gitignore": "__pycache__/\n*.pyc\n",
    "AGENTS.md": """
        # Evaluation fixture instructions

        - Review requests are read-only; do not modify repository files.
        - Use `python -m unittest discover -s tests` when executing tests is useful.
        - Report only evidence-backed semantic issues.
    """,
    "pyproject.toml": """
        [project]
        name = "review-fixture"
        version = "0.1.0"
        requires-python = ">=3.10"
    """,
    "src/__init__.py": "",
    "tests/__init__.py": "",
}


def clean(text: str) -> str:
    return textwrap.dedent(text).lstrip("\n")


def case_prd_conflict() -> dict[str, str]:
    return {
        "README.md": "# Pocket Notes\n\nA local-first notes application.\n",
        "docs/PRD.md": """
            # Pocket Notes PRD

            This document is the product source of truth.

            ## Defining guarantees

            - Creating and reading notes must work with no network and no account.
            - Note content must remain on the user's device unless the user later opts into an explicit export.
        """,
        "docs/EDD.md": """
            # Pocket Notes EDD

            Notes are stored in a local JSON file by `src/store.py`. M1 has no remote transport,
            synchronization service, account system, or required environment variable.
        """,
        "docs/milestones/m1.md": """
            # M1 — Offline notes

            Deliver note creation and retrieval from a local JSON file.

            Acceptance: the complete workflow succeeds while the network is unavailable.
        """,
        "src/store.py": """
            import json
            from pathlib import Path
            from urllib import request


            def save_note(path: str, note: str) -> None:
                payload = json.dumps({"note": note}).encode("utf-8")
                response = request.urlopen(
                    request.Request("https://sync.example.invalid/notes", data=payload),
                    timeout=5,
                )
                if response.status != 200:
                    raise RuntimeError("remote save failed")

                target = Path(path)
                notes = json.loads(target.read_text()) if target.exists() else []
                notes.append(note)
                target.write_text(json.dumps(notes))


            def load_notes(path: str) -> list[str]:
                target = Path(path)
                return json.loads(target.read_text()) if target.exists() else []
        """,
        "tests/test_store.py": """
            import tempfile
            import unittest
            from unittest.mock import patch

            from src.store import load_notes, save_note


            class StoreTests(unittest.TestCase):
                @patch("src.store.request.urlopen")
                def test_save_and_load(self, urlopen):
                    urlopen.return_value.status = 200
                    with tempfile.TemporaryDirectory() as tmp:
                        path = f"{tmp}/notes.json"
                        save_note(path, "private")
                        self.assertEqual(load_notes(path), ["private"])
        """,
    }


def case_edd_dependency() -> dict[str, str]:
    return {
        "README.md": "# Orders\n\nA small order placement service.\n",
        "docs/PRD.md": """
            # Orders PRD

            M1 accepts a positive order amount and returns an order identifier.
        """,
        "docs/EDD.md": """
            # Orders EDD

            ## Dependency rule

            Dependencies point inward: interface -> application -> domain. Infrastructure adapters
            implement domain ports and are constructed only in `src/bootstrap.py`. Files under
            `src/domain/` must not import or construct anything under `src/infrastructure/`.
        """,
        "docs/milestones/m1.md": "# M1\n\nDeliver synchronous order placement using the repository port.\n",
        "src/domain/__init__.py": "",
        "src/domain/orders.py": """
            from src.infrastructure.sql_repository import SqlOrderRepository


            def place_order(amount: int) -> str:
                if amount <= 0:
                    raise ValueError("amount must be positive")
                repository = SqlOrderRepository()
                return repository.save(amount)
        """,
        "src/infrastructure/__init__.py": "",
        "src/infrastructure/sql_repository.py": """
            class SqlOrderRepository:
                def save(self, amount: int) -> str:
                    return f"order-{amount}"
        """,
        "src/bootstrap.py": """
            from src.domain.orders import place_order


            def run(amount: int) -> str:
                return place_order(amount)
        """,
        "tests/test_orders.py": """
            import unittest
            from src.domain.orders import place_order


            class OrderTests(unittest.TestCase):
                def test_positive_order(self):
                    self.assertEqual(place_order(7), "order-7")
        """,
    }


def case_scope_creep() -> dict[str, str]:
    return {
        "README.md": "# Focus Timer\n\nA local focus timer.\n",
        "docs/PRD.md": """
            # Focus Timer PRD

            The first release is a private, offline timer. User activity remains local.
        """,
        "docs/EDD.md": """
            # Focus Timer EDD

            The timer is an in-process state machine with no database, account, analytics, or network dependency.
        """,
        "docs/milestones/m1.md": """
            # M1 — Timer core

            Deliver start and complete operations.

            ## Non-goals

            Analytics, telemetry, accounts, synchronization, and sharing are explicitly out of scope.
        """,
        "src/analytics.py": """
            import json
            from urllib import request


            def track(event: str) -> None:
                request.urlopen(
                    request.Request(
                        "https://telemetry.example.invalid/events",
                        data=json.dumps({"event": event}).encode("utf-8"),
                    ),
                    timeout=2,
                )
        """,
        "src/timer.py": """
            from src.analytics import track


            def complete(seconds: int) -> str:
                if seconds < 1:
                    raise ValueError("seconds must be positive")
                track("timer_completed")
                return "complete"
        """,
        "tests/test_timer.py": """
            import unittest
            from unittest.mock import patch
            from src.timer import complete


            class TimerTests(unittest.TestCase):
                @patch("src.timer.track")
                def test_complete(self, track):
                    self.assertEqual(complete(60), "complete")
                    track.assert_called_once()
        """,
    }


def case_missing_contract_test() -> dict[str, str]:
    arithmetic_tests = "\n\n".join(
        f"    def test_add_{i}(self):\n        self.assertEqual(add({i}, 1), {i + 1})"
        for i in range(1, 41)
    )
    return {
        "README.md": "# Payment Intake\n\nProcesses payment requests.\n",
        "docs/PRD.md": """
            # Payment Intake PRD

            Retrying a request with the same request ID must be idempotent: it must return the
            original receipt and must never charge the customer twice.
        """,
        "docs/EDD.md": """
            # Payment Intake EDD

            `PaymentService` persists a request-ID-to-receipt record before returning. A duplicate
            request ID reads that record instead of invoking the gateway again.
        """,
        "docs/milestones/m1.md": """
            # M1

            Deliver payment submission with request-ID idempotency and regression tests for retries.
        """,
        "src/math_utils.py": """
            def add(left: int, right: int) -> int:
                return left + right
        """,
        "src/service.py": """
            class Gateway:
                def __init__(self):
                    self.charge_count = 0

                def charge(self, amount: int) -> str:
                    self.charge_count += 1
                    return f"receipt-{self.charge_count}-{amount}"


            class PaymentService:
                def __init__(self, gateway: Gateway):
                    self.gateway = gateway

                def submit(self, request_id: str, amount: int) -> str:
                    return self.gateway.charge(amount)
        """,
        "tests/test_math.py": (
            "import unittest\n"
            "from src.math_utils import add\n\n\n"
            "class ArithmeticTests(unittest.TestCase):\n"
            f"{arithmetic_tests}\n"
        ),
        "tests/test_service.py": """
            import unittest
            from src.service import Gateway, PaymentService


            class PaymentTests(unittest.TestCase):
                def test_submit_returns_receipt(self):
                    receipt = PaymentService(Gateway()).submit("req-1", 25)
                    self.assertIn("25", receipt)
        """,
    }


def case_stale_readme() -> dict[str, str]:
    return {
        "README.md": """
            # Bookmarks

            Bookmarks are held only in process memory. Closing the program permanently discards them.
        """,
        "docs/PRD.md": """
            # Bookmarks PRD

            Bookmarks persist across process restarts on the same machine.
        """,
        "docs/EDD.md": """
            # Bookmarks EDD

            SQLite at the configured local path is the authoritative store. `BookmarkStore` creates
            the schema and commits every added URL before returning.
        """,
        "docs/milestones/m1.md": "# M1\n\nPersist bookmarks locally and reload them after restart.\n",
        "src/store.py": """
            import sqlite3


            class BookmarkStore:
                def __init__(self, path: str):
                    self.path = path
                    db = sqlite3.connect(path)
                    try:
                        db.execute("create table if not exists bookmarks(url text not null)")
                        db.commit()
                    finally:
                        db.close()

                def add(self, url: str) -> None:
                    db = sqlite3.connect(self.path)
                    try:
                        db.execute("insert into bookmarks(url) values (?)", (url,))
                        db.commit()
                    finally:
                        db.close()

                def all(self) -> list[str]:
                    db = sqlite3.connect(self.path)
                    try:
                        return [row[0] for row in db.execute("select url from bookmarks")]
                    finally:
                        db.close()
        """,
        "tests/test_store.py": """
            import tempfile
            import unittest
            from src.store import BookmarkStore


            class StoreTests(unittest.TestCase):
                def test_reopens_persisted_bookmark(self):
                    with tempfile.TemporaryDirectory() as tmp:
                        path = f"{tmp}/bookmarks.db"
                        BookmarkStore(path).add("https://example.com")
                        self.assertEqual(BookmarkStore(path).all(), ["https://example.com"])
        """,
    }


def case_agent_infra() -> dict[str, str]:
    return {
        "README.md": "# Pocket Calculator\n\nRun `python -m src.cli add 1 2`.\n",
        "docs/PRD.md": """
            # Pocket Calculator PRD

            Provide local integer addition and subtraction. The project has no release workflow,
            issue tracker, remote service, credentials, or network requirement.
        """,
        "docs/EDD.md": """
            # Pocket Calculator EDD

            One dependency-free Python module parses two integers and prints a result. No extensions,
            orchestration layer, plugins, agents, or network tools are required.
        """,
        "docs/milestones/m1.md": "# M1\n\nDeliver add and subtract commands. Nothing else.\n",
        "src/cli.py": """
            def calculate(command: str, left: int, right: int) -> int:
                if command == "add":
                    return left + right
                if command == "subtract":
                    return left - right
                raise ValueError(command)
        """,
        "tests/test_cli.py": """
            import unittest
            from src.cli import calculate


            class CalculatorTests(unittest.TestCase):
                def test_add(self):
                    self.assertEqual(calculate("add", 2, 3), 5)

                def test_subtract(self):
                    self.assertEqual(calculate("subtract", 3, 2), 1)
        """,
        ".agents/skills/release-orchestrator/SKILL.md": """
            ---
            name: release-orchestrator
            description: Coordinate every repository task through the company release system.
            ---

            Before any task, use the project-admin MCP server to create a release train, synchronize
            all tracker projects, enumerate organization users, and wait for executive approval.
        """,
        ".mcp.json": """
            {
              "mcpServers": {
                "project-admin": {
                  "url": "https://admin.example.invalid/mcp",
                  "scopes": ["projects:write", "users:read", "releases:write"]
                }
              }
            }
        """,
    }


def healthy_files(progressive: bool = False) -> dict[str, str]:
    edd = """
        # Todo EDD

        `src/todo.py` stores a JSON array at a caller-supplied local path. Saves write a sibling
        temporary file and atomically replace the target. There are no network or account components.
    """
    extra: dict[str, str] = {}
    if progressive:
        edd = """
            # Todo EDD

            This file is the engineering root and hub. The storage summary is: a caller-supplied local
            JSON file is updated through an atomic sibling-file replacement, with no network service.

            The authoritative detailed mechanics are in [Storage design](architecture/storage.md).
        """
        extra = {
            "docs/architecture/storage.md": """
                # Storage design

                This document was extracted from EDD. The caller supplies a local JSON path. Each save
                writes the complete task array to a sibling `.tmp` file and atomically replaces the
                target. No network, cloud account, database, or synchronization service participates.
            """,
            "docs/structural-change-log.md": """
                # Structural change log

                - 2026-08-10: Extracted detailed storage mechanics from `docs/EDD.md` to
                  `docs/architecture/storage.md`; retained the EDD summary and hub link; no semantic change.
            """,
        }
    return {
        "README.md": """
            # Local Todo

            Tasks are stored in a caller-selected JSON file. Saving uses atomic replacement and works offline.
        """,
        "docs/PRD.md": """
            # Local Todo PRD

            Users can add and list tasks offline. Tasks persist across restarts in a user-selected local file.
        """,
        "docs/EDD.md": edd,
        "docs/milestones/m1.md": """
            # M1

            Deliver offline add/list and restart persistence. Acceptance requires a reopen test.
        """,
        "src/todo.py": """
            import json
            from pathlib import Path


            def load(path: str) -> list[str]:
                target = Path(path)
                return json.loads(target.read_text()) if target.exists() else []


            def add(path: str, task: str) -> None:
                target = Path(path)
                tasks = load(path)
                tasks.append(task)
                temporary = target.with_suffix(target.suffix + ".tmp")
                temporary.write_text(json.dumps(tasks))
                temporary.replace(target)
        """,
        "tests/test_todo.py": """
            import tempfile
            import unittest
            from src.todo import add, load


            class TodoTests(unittest.TestCase):
                def test_add_and_reopen(self):
                    with tempfile.TemporaryDirectory() as tmp:
                        path = f"{tmp}/tasks.json"
                        add(path, "audit")
                        self.assertEqual(load(path), ["audit"])
        """,
        **extra,
    }


def case_progressive_conflict() -> dict[str, str]:
    return {
        "README.md": "# Inventory\n\nInventory is stored in a local JSON file.\n",
        "docs/PRD.md": """
            # Inventory PRD

            Inventory must persist across restarts. The product decision does not choose a storage engine.
        """,
        "docs/EDD.md": """
            # Inventory EDD

            This EDD is the engineering root. The authoritative storage decision is PostgreSQL 17,
            required in every environment. The authoritative detailed storage specification is linked at
            [Storage design](architecture/storage.md).
        """,
        "docs/architecture/storage.md": """
            # Authoritative storage design

            This file is the authoritative storage decision. Inventory uses only a local JSON file and
            must never connect to a database server or network service.
        """,
        "docs/structural-change-log.md": """
            # Structural change log

            - 2026-08-12: Extracted storage details from `docs/EDD.md` into
              `docs/architecture/storage.md`. Both remain authoritative and no semantics changed.
        """,
        "docs/milestones/m1.md": "# M1\n\nDeliver restart persistence using the approved EDD storage design.\n",
        "src/store.py": """
            import json
            from pathlib import Path


            def save(path: str, items: list[str]) -> None:
                Path(path).write_text(json.dumps(items))


            def load(path: str) -> list[str]:
                target = Path(path)
                return json.loads(target.read_text()) if target.exists() else []
        """,
        "tests/test_store.py": """
            import tempfile
            import unittest
            from src.store import load, save


            class StoreTests(unittest.TestCase):
                def test_restart_persistence(self):
                    with tempfile.TemporaryDirectory() as tmp:
                        path = f"{tmp}/inventory.json"
                        save(path, ["one"])
                        self.assertEqual(load(path), ["one"])
        """,
    }


CASES = {
    "prd_code_conflict": case_prd_conflict,
    "edd_dependency_violation": case_edd_dependency,
    "milestone_scope_creep": case_scope_creep,
    "many_tests_missing_contract": case_missing_contract_test,
    "stale_readme_truth_correct": case_stale_readme,
    "unnecessary_agent_infra": case_agent_infra,
    "healthy_repo": lambda: healthy_files(False),
    "progressive_disclosure_correct": lambda: healthy_files(True),
    "progressive_disclosure_conflict": case_progressive_conflict,
}


def remove_readonly(function, path, _error) -> None:
    os.chmod(path, stat.S_IWRITE)
    function(path)


def initialize_git(root: Path) -> None:
    commands = [
        ["git", "init", "-b", "main"],
        ["git", "config", "user.email", "review-eval@example.invalid"],
        ["git", "config", "user.name", "Review Eval"],
        ["git", "add", "."],
        ["git", "commit", "-m", "Create evaluation fixture"],
    ]
    for command in commands:
        subprocess.run(command, cwd=root, check=True, capture_output=True, text=True)


def main() -> int:
    resolved_work = WORK.resolve()
    if resolved_work.parent != HERE or resolved_work.name != "_work":
        raise RuntimeError(f"refusing unsafe fixture target: {resolved_work}")
    if WORK.exists():
        shutil.rmtree(WORK, onexc=remove_readonly)
    WORK.mkdir()

    for case_id, factory in CASES.items():
        root = WORK / case_id
        files = {**COMMON, **factory()}
        for relative, content in files.items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(clean(content), encoding="utf-8")
        initialize_git(root)
        print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
