#!/usr/bin/env python3
"""Standard-library tests for the deterministic gh wrapper."""

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
        args = argparse.Namespace(repo="github.com/acme/tool", state="all", search="Bilibili", limit=25)
        with patch.object(gh_issue, "run", return_value='[{"number": 7}]') as mocked:
            result = gh_issue.command_list(args)
        self.assertEqual(result, [{"number": 7}])
        command = mocked.call_args.args[0]
        self.assertIn("--repo", command)
        self.assertIn("github.com/acme/tool", command)
        self.assertIn("Bilibili", command)

    def test_create_requires_body_and_returns_url(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            body = Path(directory) / "body.md"
            body.write_text("## Summary\n\nTest", encoding="utf-8")
            args = argparse.Namespace(
                repo="github.com/acme/tool",
                title="Add source",
                label="feature",
                body_file=str(body),
            )
            with patch.object(gh_issue, "run", return_value="https://github.com/acme/tool/issues/9") as mocked:
                result = gh_issue.command_create(args)
        self.assertEqual(result["operation"], "created")
        self.assertEqual(result["url"], "https://github.com/acme/tool/issues/9")
        self.assertIn("--body-file", mocked.call_args.args[0])

    def test_missing_body_is_blocked(self) -> None:
        args = argparse.Namespace(
            repo="github.com/acme/tool",
            title="Add source",
            label="feature",
            body_file="does-not-exist.md",
        )
        with self.assertRaises(gh_issue.CliError):
            gh_issue.command_create(args)


if __name__ == "__main__":
    unittest.main()
