#!/usr/bin/env python3
"""Tests for deterministic GitHub collaboration template rendering."""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
import unittest

from render_github_templates import render, rendered_assets


class GitHubTemplateTests(unittest.TestCase):
    def test_render_creates_refs_template_and_configured_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            render(root, 'Build "and" Test', overwrite=False, dry_run=False)

            template = (root / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
            workflow = (root / ".github" / "workflows" / "issue-finalize.yml").read_text(encoding="utf-8")
            script = root / ".github" / "scripts" / "issue-finalize.js"

            self.assertIn("Refs #<number>", template)
            self.assertIn("one final delivery PR", template)
            self.assertIsNone(re.search(r"(?mi)^\s*(?:Closes|Fixes|Resolves)\s+#", template))
            self.assertIsNone(re.search(r"(?mi)^\s*(?:Delivers|Completes)\s+#", template))
            self.assertIn('workflows: ["Build \\"and\\" Test"]', workflow)
            self.assertNotIn("__MAIN_CI_WORKFLOW_NAME__", workflow)
            self.assertTrue(script.is_file())

    def test_dry_run_has_no_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / ".github" / "PULL_REQUEST_TEMPLATE.md"
            target.parent.mkdir(parents=True)
            target.write_text("custom\n", encoding="utf-8")
            result = render(root, "CI", overwrite=False, dry_run=True)
            self.assertTrue(result["dry_run"])
            self.assertEqual(result["conflicts"], [str(Path(".github/PULL_REQUEST_TEMPLATE.md"))])
            self.assertEqual(target.read_text(encoding="utf-8"), "custom\n")
            self.assertFalse((root / ".github" / "workflows").exists())

    def test_existing_different_file_requires_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / ".github" / "PULL_REQUEST_TEMPLATE.md"
            target.parent.mkdir(parents=True)
            target.write_text("custom\n", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                render(root, "CI", overwrite=False, dry_run=False)
            self.assertEqual(target.read_text(encoding="utf-8"), "custom\n")

    def test_multiple_refs_are_supported_by_runtime_asset(self) -> None:
        script = rendered_assets("CI")[Path(".github/scripts/issue-finalize.js")]
        self.assertIn("new Set()", script)
        self.assertIn("parseIssueReferences", script)

    def test_workflow_has_lifecycle_guards_and_least_privilege(self) -> None:
        workflow = rendered_assets("CI")[Path(".github/workflows/issue-finalize.yml")]
        for phrase in (
            "workflow_run:",
            "types: [completed]",
            "workflow_run.event == 'push'",
            "workflow_run.head_branch == github.event.repository.default_branch",
            "contents: read",
            "pull-requests: read",
            "issues: write",
        ):
            self.assertIn(phrase, workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
