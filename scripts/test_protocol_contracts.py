#!/usr/bin/env python3
"""Deterministic semantic checks for the Issue-driven, PR-first protocol library."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ProtocolContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_exact_skill_inventory(self) -> None:
        actual = {path.name for path in (ROOT / "skills").iterdir() if path.is_dir() and (path / "SKILL.md").is_file()}
        self.assertEqual(actual, {"bootstrap-repo", "create-issue", "fix-bug", "review-repo"})

    def test_root_authority_and_pr_contract(self) -> None:
        agents = self.read("AGENTS.md")
        template = self.read(".github/PULL_REQUEST_TEMPLATE.md")
        self.assertIn("Issue", agents)
        self.assertIn("PRD", agents)
        self.assertIn("EDD", agents)
        for heading in ("Issue", "What changed", "Verification", "Contract impact"):
            self.assertIn(heading, template)

    def test_bootstrap_requires_only_prd_edd_and_pr_first_handoff(self) -> None:
        skill = self.read("skills/bootstrap-repo/SKILL.md")
        workflow = self.read("skills/bootstrap-repo/references/workflow.md")
        self.assertIn("docs/PRD.md", skill)
        self.assertIn("docs/EDD.md", skill)
        self.assertIn("Issue-backed changes normally use an isolated branch or worktree", skill)
        self.assertIn("without private conversation state", skill)
        self.assertIn("Required verification must pass before merge", skill)
        self.assertIn("Issue → branch/worktree → implementation → commit → push → PR", workflow)

    def test_create_issue_semantic_manifest(self) -> None:
        manifest = json.loads(self.read("skills/create-issue/evals/manifest.json"))
        self.assertEqual(manifest["source_modes"], ["human-settled-intent", "review-finding"])
        self.assertEqual(manifest["types"], ["bug", "feature", "enhancement"])
        self.assertEqual(len(manifest["review_finding_gate"]), 6)

    def test_create_issue_guards_human_intent_and_semantic_conflicts(self) -> None:
        skill = self.read("skills/create-issue/SKILL.md")
        self.assertIn("Only settled human intent becomes a Work Contract", skill)
        self.assertIn("would change PRD/EDD semantics", skill)
        self.assertIn("do not create an Issue that chooses the design", skill)
        self.assertIn("search both open and closed Issues", skill)

    def test_create_issue_review_mode_has_parallelism_hints_not_types(self) -> None:
        skill = self.read("skills/create-issue/SKILL.md")
        self.assertIn("review-finding", skill)
        self.assertIn("parallel:candidate", skill)
        self.assertIn("These are not Issue types", skill)

    def test_fix_bug_adopts_bug_issue_and_emits_pr_evidence(self) -> None:
        skill = self.read("skills/fix-bug/SKILL.md")
        manifest = json.loads(self.read("skills/fix-bug/evals/manifest.json"))
        self.assertIn("Automatically adopt", skill)
        self.assertTrue(manifest["issue_backed_bug_auto_adoption"])
        self.assertIn("pr-handoff", manifest["execution_protocol"])
        self.assertIn("reproduce -> prove -> diagnose -> regression test -> minimal fix -> verify -> broader regression check", skill)
        self.assertIn("does not own task scheduling", skill.lower())
        self.assertIn("repository-wide review", skill.lower())

    def test_review_repo_has_issue_pr_provenance_and_guard(self) -> None:
        skill = self.read("skills/review-repo/SKILL.md")
        schema = json.loads(self.read("skills/review-repo/evals/output-schema.json"))
        self.assertIn("Issue/PR provenance", skill)
        self.assertIn("six gates", skill)
        self.assertIn("issue_pr_provenance_status", schema["required"])
        self.assertIn("issue_candidates", schema["required"])

    def test_review_repo_is_independent_and_source_read_only(self) -> None:
        skill = self.read("skills/review-repo/SKILL.md")
        self.assertIn("independent", skill)
        self.assertIn("source tree and human-owned PRD/EDD stay read-only", skill)
        self.assertIn("not the final review step of another skill", skill)
        self.assertIn("across multiple accepted PRs", skill)

    def test_review_to_issue_link_requires_all_guards(self) -> None:
        skill = self.read("skills/review-repo/SKILL.md")
        for phrase in (
            "direct evidence is sufficient",
            "consequence is material",
            "remedy is bounded",
            "confidence is high",
            "open and closed Issue search found no equivalent",
            "does not require an unapproved PRD/EDD semantic change",
        ):
            self.assertIn(phrase, skill)

    def test_discovery_mirror_is_byte_identical(self) -> None:
        source = ROOT / "skills" / "create-issue"
        mirror = ROOT / ".agents" / "skills" / "create-issue"
        source_files = {p.relative_to(source) for p in source.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        mirror_files = {p.relative_to(mirror) for p in mirror.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        self.assertEqual(source_files, mirror_files)
        for relative in source_files:
            self.assertEqual((source / relative).read_bytes(), (mirror / relative).read_bytes(), str(relative))

    def test_ci_matches_deterministic_four_skill_checks(self) -> None:
        workflow = self.read(".github/workflows/ci.yml")
        for command in (
            "python scripts/validate_skills.py",
            "python scripts/test_protocol_contracts.py",
            "python skills/bootstrap-repo/scripts/test_inspect_repo.py",
            "python skills/create-issue/scripts/test_gh_issue.py",
        ):
            self.assertIn(command, workflow)

    def test_no_runtime_skill_uses_retired_delivery_model(self) -> None:
        retired_name = "implement-" + "mile" + "stone"
        retired_term = "mile" + "stone"
        for root in (ROOT / "skills", ROOT / "docs", ROOT / "README.md", ROOT / "AGENTS.md"):
            paths = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]
            for path in paths:
                if "_work" in path.parts or "__pycache__" in path.parts or path.suffix == ".log":
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
                self.assertNotIn(retired_name, text, str(path.relative_to(ROOT)))
                self.assertNotIn(retired_term, text, str(path.relative_to(ROOT)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
