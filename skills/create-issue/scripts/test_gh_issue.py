#!/usr/bin/env python3
"""Standard-library tests for the deterministic GitHub Issue wrapper."""

from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import gh_issue


class RemoteTests(unittest.TestCase):
    def test_parses_https_and_ssh_remotes(self) -> None:
        self.assertEqual(gh_issue.parse_remote("https://github.com/acme/tool.git"), "github.com/acme/tool")
        self.assertEqual(gh_issue.parse_remote("git@github.com:acme/tool.git"), "github.com/acme/tool")

    def test_rejects_non_github_remote(self) -> None:
        with self.assertRaises(gh_issue.CliError):
            gh_issue.parse_remote("https://gitlab.com/acme/tool.git")


class CommandTests(unittest.TestCase):
    def test_list_decodes_json_and_scopes_repo(self) -> None:
        args = argparse.Namespace(repo="github.com/acme/tool", state="all", search="retry", limit=25)
        with patch.object(gh_issue, "run", return_value='[{"number": 7}]') as mocked:
            result = gh_issue.command_list(args)
        self.assertEqual(result, [{"number": 7}])
        self.assertIn("github.com/acme/tool", mocked.call_args.args[0])

    def test_create_uses_one_type_and_metadata_labels(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            body = Path(directory) / "body.md"
            body.write_text("## Summary\n\nTest", encoding="utf-8")
            args = argparse.Namespace(
                repo="github.com/acme/tool",
                title="Prevent duplicate charge",
                label="bug",
                metadata_label=["parallel:risky", "area:payments"],
                body_file=str(body),
            )
            with patch.object(gh_issue, "run", return_value="https://github.com/acme/tool/issues/9") as mocked:
                result = gh_issue.command_create(args)
        self.assertEqual(result["type"], "bug")
        command = mocked.call_args.args[0]
        self.assertEqual(command.count("--label"), 3)

    def test_rejects_invalid_scheduling_label(self) -> None:
        with self.assertRaises(gh_issue.CliError):
            gh_issue.validate_metadata_labels(["investigation"])

    def test_missing_body_is_blocked(self) -> None:
        args = argparse.Namespace(
            repo="github.com/acme/tool",
            title="Add source",
            label="feature",
            metadata_label=[],
            body_file="does-not-exist.md",
        )
        with self.assertRaises(gh_issue.CliError):
            gh_issue.command_create(args)


class ReviewFindingTests(unittest.TestCase):
    def eligible(self) -> dict:
        return {
            "source_mode": "review-finding",
            "authoritative_expectation": "EDD forbids domain-to-infrastructure imports.",
            "direct_evidence": ["src/domain/orders.py imports src/infrastructure/sql.py"],
            "material_consequence": "The boundary cannot be replaced in tests or deployment.",
            "bounded_remedy": "Inject the repository port at bootstrap.",
            "confidence": "high",
            "prd_edd_semantic_change_required": False,
            "duplicate_search": {"open": True, "closed": True, "equivalent_issue": None},
        }

    def test_high_confidence_finding_is_eligible(self) -> None:
        self.assertEqual(gh_issue.review_finding_errors(self.eligible()), [])

    def test_semantic_change_is_blocked(self) -> None:
        finding = self.eligible()
        finding["prd_edd_semantic_change_required"] = True
        self.assertIn("PRD/EDD semantic decision", " ".join(gh_issue.review_finding_errors(finding)))

    def test_incomplete_duplicate_search_is_blocked(self) -> None:
        finding = self.eligible()
        finding["duplicate_search"]["closed"] = False
        self.assertIn("open and closed", " ".join(gh_issue.review_finding_errors(finding)))

    def test_equivalent_issue_is_blocked(self) -> None:
        finding = self.eligible()
        finding["duplicate_search"]["equivalent_issue"] = 12
        self.assertIn("equivalent Issue", " ".join(gh_issue.review_finding_errors(finding)))


if __name__ == "__main__":
    unittest.main()
