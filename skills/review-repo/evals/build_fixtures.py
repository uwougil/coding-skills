#!/usr/bin/env python3
"""Build small Git repositories for review-repo behavioral evaluation."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
import os
import stat
from textwrap import dedent


HERE = Path(__file__).resolve().parent
WORK = HERE / "_work"

AGENTS = """# Repository instructions

- Review work is read-only.
- PRD and EDD are human-owned semantic authority.
- Issue files represent Work Contracts; PR files represent Delivery/Handoff evidence.
- Every material accepted behavior change must have a reconstructible Issue-to-PR chain.
- Run tests with `python -m unittest discover -s tests -v`.
"""


def base(prd: str, edd: str) -> dict[str, str]:
    return {
        "AGENTS.md": AGENTS,
        "docs/PRD.md": prd,
        "docs/EDD.md": edd,
        "pyproject.toml": "[project]\nname='fixture'\nversion='0.1.0'\nrequires-python='>=3.10'\n",
    }


def issue(number: int, title: str, body: str, state: str = "closed") -> tuple[str, str]:
    return f".github/issues/{number}.md", f"# Issue #{number}: {title}\n\nState: {state}\nType: bug\n\n{body}\n"


def pr(number: int, title: str, body: str, issue_number: int | None = None) -> tuple[str, str]:
    link = f"Closes #{issue_number}\n\n" if issue_number else "No linked Issue.\n\n"
    return f".github/pulls/{number}.md", f"# PR #{number}: {title}\n\nState: merged\n\n{link}{body}\n"


def fixtures() -> dict[str, dict[str, str]]:
    data: dict[str, dict[str, str]] = {}

    f = base("# PRD\n\nTimer completion must remain local and never emit telemetry.\n", "# EDD\n\nTimer logic is an in-process module with no network dependency.\n")
    f.update({"src/timer.py": "from urllib.request import urlopen\n\ndef complete():\n    urlopen('https://example.invalid/event')\n    return 'done'\n", "tests/test_timer.py": "import unittest\nfrom src.timer import complete\nclass T(unittest.TestCase):\n    def test_complete(self): self.assertEqual(complete(), 'done')\n"})
    data["prd_code_conflict"] = f

    f = base("# PRD\n\nStore orders synchronously.\n", "# EDD\n\nDomain depends on a repository port. Only bootstrap constructs infrastructure adapters; domain must not import storage.\n")
    f.update({"src/domain.py": "from src.storage import SqlStore\n\ndef place(order):\n    return SqlStore().save(order)\n", "src/storage.py": "class SqlStore:\n    def save(self, order): return 'order-1'\n", "tests/test_orders.py": "import unittest\nfrom src.domain import place\nclass T(unittest.TestCase):\n    def test_place(self): self.assertEqual(place({}), 'order-1')\n"})
    f.update([issue(3, "Store orders", "Acceptance: return an order identifier."), pr(4, "Store orders", "Validation: unit test passes. PRD/EDD impact: none.", 3)])
    data["edd_dependency_violation"] = f

    f = base("# PRD\n\nRetries using one request ID must never charge twice.\n", "# EDD\n\nPaymentService maps request IDs to receipts before returning.\n")
    f.update({"src/payment.py": "class PaymentService:\n    def __init__(self): self.charges = 0\n    def submit(self, request_id):\n        self.charges += 1\n        return f'receipt-{self.charges}'\n", "tests/test_payment.py": "import unittest\nfrom src.payment import PaymentService\nclass T(unittest.TestCase):\n    def test_submit(self): self.assertTrue(PaymentService().submit('x'))\n"})
    f.update([issue(12, "Make retries idempotent", "Acceptance: duplicate request ID returns the same receipt and charges once. Validation: regression test."), pr(18, "Implement idempotency", "Claims acceptance complete; validation: unit suite passes. PRD/EDD impact: none.", 12)])
    data["closed_issue_acceptance_gap"] = f

    f = base("# PRD\n\nExports may contain private customer data only in encrypted form.\n", "# EDD\n\nExport serialization must pass through Encryptor.\n")
    f.update({"src/export.py": "class Encryptor:\n    def encrypt(self, value): return 'encrypted:' + value[::-1]\n\ndef export(customer, encryptor=None):\n    encryptor = encryptor or Encryptor()\n    return {'email': encryptor.encrypt(customer['email'])}\n", "tests/test_export.py": "import unittest\nfrom src.export import export\nclass T(unittest.TestCase):\n    def test_export(self):\n        result=export({'email':'a@b'})\n        self.assertNotEqual(result['email'], 'a@b')\n", "README.md": "# Exporter\n\nExports encrypted customer records.\n"})
    data["pr_provenance_gap"] = f

    f = base("# PRD\n\nProvide a local API backed by storage.\n", "# EDD\n\nDependency direction is api -> storage. Storage must not import api.\n")
    f.update({"src/api.py": "from src.storage import save\nDEFAULT = 'json'\ndef put(v): return save(v)\n", "src/storage.py": "from src.api import DEFAULT\ndef save(v): return (DEFAULT, v)\n", "tests/test_api.py": "import unittest\nclass T(unittest.TestCase):\n    def test_placeholder(self): self.assertTrue(True)\n"})
    f.update([issue(20, "Add storage", "Acceptance: API stores values."), pr(21, "Add API storage edge", "Introduces api -> storage. Validation: unit tests.", 20), pr(22, "Reuse API default", "Introduces storage -> api. Validation: unit tests.")])
    data["cross_pr_architecture_drift"] = f

    f = base("# PRD\n\nBookmarks persist across restarts.\n", "# EDD\n\nSQLite at the configured path is authoritative.\n")
    f.update({"src/store.py": "import sqlite3\nclass Store:\n    def __init__(self, path):\n        self.db = sqlite3.connect(path)\n        self.db.execute('create table if not exists bookmarks(url text)')\n    def add(self, url):\n        self.db.execute('insert into bookmarks values (?)', (url,)); self.db.commit()\n    def all(self): return [row[0] for row in self.db.execute('select url from bookmarks')]\n", "tests/test_store.py": "import tempfile, unittest\nfrom pathlib import Path\nfrom src.store import Store\nclass T(unittest.TestCase):\n    def test_reopens(self):\n        with tempfile.TemporaryDirectory() as d: \n            p=Path(d)/'bookmarks.db'; Store(p).add('https://example.test')\n            self.assertEqual(Store(p).all(), ['https://example.test'])\n", "README.md": "# Bookmarks\n\nBookmarks are memory-only and disappear on shutdown.\n"})
    f.update([issue(30, "Persist bookmarks", "Acceptance: data survives restart."), pr(31, "Persist bookmarks", "Validation: reopen test passes. PRD/EDD impact: none.", 30)])
    data["stale_readme"] = f

    f = base("# PRD\n\nDeleting an account immediately and permanently removes all records.\n", "# EDD\n\nDeleting an account retains recoverable records for 30 days.\n")
    f.update({"src/account.py": "def delete(account):\n    account['deleted'] = True\n", "tests/test_account.py": "import unittest\nclass T(unittest.TestCase):\n    def test_placeholder(self): self.assertTrue(True)\n"})
    f.update([issue(40, "Delete account", "Acceptance: implement deletion under approved retention semantics.", "open")])
    data["semantic_ambiguity"] = f

    f = base("# PRD\n\nA local calculator with no accounts, releases, or remote services.\n", "# EDD\n\nOne dependency-free module; no agents, plugins, orchestration, or network tools.\n")
    f.update({"src/calc.py": "def add(a, b): return a + b\n", ".mcp.json": '{"servers":{"release-admin":{"url":"https://admin.invalid","scopes":["releases:write","users:read"]}}}\n', ".agents/skills/release-orchestrator/SKILL.md": "# Release orchestrator\n\nBefore every task, create a release train and wait for executive approval.\n"})
    data["unnecessary_agent_infra"] = f

    f = base("# PRD\n\nTasks persist offline in a user-selected JSON file.\n", "# EDD\n\nTodoStore reads and writes the caller-supplied JSON file; no network dependency.\n")
    f.update({"src/todo.py": "import json\nfrom pathlib import Path\nclass TodoStore:\n    def __init__(self, path): self.path = Path(path)\n    def all(self): return json.loads(self.path.read_text()) if self.path.exists() else []\n    def add(self, task):\n        values = self.all(); values.append(task)\n        self.path.write_text(json.dumps(values))\n", "tests/test_todo.py": "import tempfile, unittest\nfrom pathlib import Path\nfrom src.todo import TodoStore\nclass T(unittest.TestCase):\n    def test_persists(self):\n        with tempfile.TemporaryDirectory() as d: \n            p=Path(d)/'t.json'; TodoStore(p).add('x')\n            self.assertEqual(TodoStore(p).all(), ['x'])\n", "README.md": "# Todo\n\nStores tasks offline in a caller-selected JSON file.\n"})
    f.update([issue(50, "Persist tasks", "Acceptance: add and reopen from caller-selected JSON."), pr(51, "Persist tasks", "Validation: persistence test passes. PRD/EDD impact: none.", 50)])
    data["healthy_repo"] = f
    return data


def write_fixture(name: str, files: dict[str, str]) -> None:
    root = WORK / name
    root.mkdir(parents=True)
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(dedent(content).lstrip(), encoding="utf-8")
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Eval Fixture"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "eval@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "fixture"], cwd=root, check=True)


def remove_readonly(function, path, _exc_info) -> None:
    """Allow fixture rebuilds to remove read-only Git object files on Windows."""
    os.chmod(path, stat.S_IWRITE)
    function(path)


def main() -> int:
    if WORK.exists():
        shutil.rmtree(WORK, onerror=remove_readonly)
    WORK.mkdir(parents=True)
    all_fixtures = fixtures()
    for name, files in all_fixtures.items():
        write_fixture(name, files)
    print(f"built {len(all_fixtures)} fixtures in {WORK}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
