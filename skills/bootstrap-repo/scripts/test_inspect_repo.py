#!/usr/bin/env python3
"""Regression tests for the read-only repository probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from inspect_repo import build_snapshot, redact_remote


class InspectRepoTests(unittest.TestCase):
    def test_prd_edd_only_is_new_bootstrap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "docs" / "PRD.md").write_text("Python CLI product", encoding="utf-8")
            (root / "docs" / "EDD.md").write_text("Use Python", encoding="utf-8")

            snapshot = build_snapshot(root)

            self.assertEqual(snapshot["suggested_mode"], "new-bootstrap")
            self.assertEqual(snapshot["intent"], {"prd": True, "edd": True, "draft_candidates": []})

    def test_existing_implementation_is_rebootstrap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src" / "index.ts").write_text("export {};\n", encoding="utf-8")
            snapshot = build_snapshot(root)
            self.assertEqual(snapshot["suggested_mode"], "existing-re-bootstrap")
            self.assertEqual(snapshot["source_file_count"], 1)

    def test_manifest_without_implementation_remains_new_bootstrap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package.json").write_text("{}\n", encoding="utf-8")
            snapshot = build_snapshot(root)
            self.assertEqual(snapshot["suggested_mode"], "new-bootstrap")
            self.assertEqual(snapshot["stack_markers"], {"node": ["package.json"]})

    def test_pr_template_and_agent_infrastructure_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".agents" / "skills" / "release").mkdir(parents=True)
            (root / ".github").mkdir()
            (root / ".agents" / "skills" / "release" / "SKILL.md").write_text("---\n", encoding="utf-8")
            (root / ".github" / "PULL_REQUEST_TEMPLATE.md").write_text("## Issue\n", encoding="utf-8")
            snapshot = build_snapshot(root)
            self.assertTrue(snapshot["delivery_contract"]["pull_request_template"])
            self.assertEqual(snapshot["agent_infrastructure"]["project_skills"], [".agents/skills/release/SKILL.md"])

    def test_url_userinfo_is_redacted(self) -> None:
        self.assertEqual(
            redact_remote("https://user:secret@example.com/owner/repo.git"),
            "https://<redacted>@example.com/owner/repo.git",
        )


if __name__ == "__main__":
    unittest.main()
