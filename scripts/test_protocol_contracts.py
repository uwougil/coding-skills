#!/usr/bin/env python3
"""Deterministic semantic checks for the Issue-driven, PR-first protocol library."""

from __future__ import annotations

import json
from pathlib import Path
import re
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
            if heading == "What changed":
                self.assertIn("修改内容", template)
            elif heading == "Verification":
                self.assertIn("验证", template)
            elif heading == "Contract impact":
                self.assertIn("契约影响", template)
            else:
                self.assertIn(heading, template)

    def test_one_issue_normally_maps_to_one_final_delivery_pr_across_layers(self) -> None:
        paths = (
            "README.md",
            "AGENTS.md",
            "docs/PRD.md",
            "docs/EDD.md",
            "skills/bootstrap-repo/SKILL.md",
            "skills/bootstrap-repo/references/workflow.md",
            "skills/create-issue/SKILL.md",
            "skills/fix-bug/SKILL.md",
            "skills/review-repo/SKILL.md",
        )
        for path in paths:
            text = self.read(path).lower()
            self.assertIn("issue", text, path)
            if path == "README.md":
                self.assertIn("可独立交付", self.read(path), path)
                self.assertIn("最终交付 pr", text, path)
            else:
                self.assertIn("independently deliverable", text, path)
                self.assertRegex(text, r"final delivery (?:pull request|pr)", path)

        create_issue = self.read("skills/create-issue/SKILL.md").lower()
        self.assertIn("revisit the issue boundary before writing", create_issue)
        self.assertIn("multiple ordinary prs", create_issue)
        review_repo = self.read("skills/review-repo/SKILL.md")
        self.assertIn("Issue -> final delivery PR -> merge commit -> main -> Main CI -> closed Issue history", review_repo)

    def test_collaboration_language_policy_is_explicit_portable_and_preserves_technical_strings(self) -> None:
        agents = self.read("AGENTS.md")
        bootstrap = self.read("skills/bootstrap-repo/SKILL.md")
        workflow = self.read("skills/bootstrap-repo/references/workflow.md")
        create_issue = self.read("skills/create-issue/SKILL.md")
        fix_bug = self.read("skills/fix-bug/SKILL.md")
        review_repo = self.read("skills/review-repo/SKILL.md")
        cases = json.loads(self.read("skills/create-issue/evals/language-cases.json"))

        for text in (bootstrap, create_issue):
            lowered = text.lower()
            for phrase in ("explicit", "agents.md", "prd/edd", "technical", "identifier", "command", "url"):
                self.assertIn(phrase, lowered)
        for phrase in ("显式", "prd", "edd", "技术术语", "标识符", "命令", "url"):
            self.assertIn(phrase, agents.lower())
        self.assertIn("never hardcode chinese", bootstrap.lower())
        self.assertIn("never hardcode chinese", create_issue.lower())
        self.assertIn("english and other repository languages", bootstrap.lower())
        self.assertIn("propagate the resolved language", workflow.lower())
        self.assertIn("resolved collaboration language", fix_bug.lower())
        self.assertIn("resolved collaboration language", review_repo.lower())

        self.assertEqual(cases["protocol"], "collaboration-language-v1")
        self.assertEqual([case["id"] for case in cases["cases"]], ["A", "B", "C", "D", "E"])
        self.assertEqual(cases["cases"][0]["expected_prose_language"], "zh-CN")
        self.assertEqual(cases["cases"][1]["expected_prose_language"], "en")
        self.assertEqual(cases["cases"][2]["expected_prose_language"], "en")
        self.assertIn("python -m pytest tests/test_editor.py", cases["cases"][4]["preserve"])
        self.assertIn("https://github.com/uwougil/coding-skills/issues/123", cases["cases"][4]["preserve"])

    def test_bootstrap_requires_only_prd_edd_and_pr_first_handoff(self) -> None:
        skill = self.read("skills/bootstrap-repo/SKILL.md")
        workflow = self.read("skills/bootstrap-repo/references/workflow.md")
        self.assertIn("docs/PRD.md", skill)
        self.assertIn("docs/EDD.md", skill)
        self.assertIn("Issue-backed changes normally use an isolated branch or worktree", skill)
        self.assertIn("without private conversation state", skill)
        self.assertIn("Required verification must pass before merge", skill)
        self.assertIn("Issue → branch/worktree → implementation → commit → push → final delivery PR", workflow)

    def test_bootstrap_main_ci_finalizes_linked_issues_without_merge_autoclose(self) -> None:
        skill = self.read("skills/bootstrap-repo/SKILL.md")
        workflow_doc = self.read("skills/bootstrap-repo/references/workflow.md")
        finalization_doc = self.read("skills/bootstrap-repo/references/issue-finalization.md")
        root_template = self.read(".github/PULL_REQUEST_TEMPLATE.md")
        asset_template = self.read("skills/bootstrap-repo/assets/github/PULL_REQUEST_TEMPLATE.md")
        root_workflow = self.read(".github/workflows/issue-finalize.yml")
        asset_workflow = self.read("skills/bootstrap-repo/assets/github/workflows/issue-finalize.yml")
        script = self.read("skills/bootstrap-repo/assets/github/scripts/issue-finalize.js")

        for template in (root_template, asset_template):
            self.assertIn("Refs #<number>", template)
            if template is root_template:
                self.assertIn("一个最终交付 PR", template)
            else:
                self.assertIn("One Issue is normally completed by one final delivery PR", template)
            self.assertIsNone(re.search(r"(?mi)^\s*(?:Closes|Fixes|Resolves)\s+#", template))
            self.assertIsNone(re.search(r"(?mi)^\s*(?:Delivers|Completes)\s+#", template))
        for text in (skill, workflow_doc, finalization_doc):
            self.assertIn("merge", text.lower())
            self.assertIn("main ci", text.lower())
            self.assertIn("refs #n", text.lower())
        self.assertIn("For every new GitHub repository bootstrap", skill)

        self.assertEqual(
            asset_workflow.replace('"__MAIN_CI_WORKFLOW_NAME__"', '"Validate skills"'),
            root_workflow,
        )
        for phrase in (
            "workflow_run:",
            "types: [completed]",
            "workflow_run.event == 'push'",
            "workflow_run.head_branch == github.event.repository.default_branch",
            "contents: read",
            "pull-requests: read",
            "issues: write",
        ):
            self.assertIn(phrase, asset_workflow)
        for phrase in (
            "listPullRequestsAssociatedWithCommit",
            "merge_commit_sha === run.head_sha",
            "issue.pull_request",
            "issue.state !== 'open'",
            "state_reason: 'completed'",
            "run_attempt",
            "github.paginate",
        ):
            self.assertIn(phrase, script)
        self.assertNotIn("issues.delete", script)
        self.assertNotIn("deleteIssue", script)

    def test_only_refs_lines_can_link_and_no_completion_syntax_is_active(self) -> None:
        protocol_paths = (
            "AGENTS.md",
            "docs/PRD.md",
            "docs/EDD.md",
            ".github/PULL_REQUEST_TEMPLATE.md",
            "skills/bootstrap-repo/SKILL.md",
            "skills/bootstrap-repo/references/workflow.md",
            "skills/bootstrap-repo/references/github.md",
            "skills/bootstrap-repo/references/issue-finalization.md",
            "skills/bootstrap-repo/assets/github/PULL_REQUEST_TEMPLATE.md",
            "skills/create-issue/SKILL.md",
            "skills/fix-bug/SKILL.md",
            "skills/review-repo/SKILL.md",
        )
        active_completion = re.compile(r"(?mi)^\s*(?:Closes|Fixes|Resolves|Delivers|Completes)\s+#\d+\s*$")
        for path in protocol_paths:
            text = self.read(path)
            self.assertIsNone(active_completion.search(text), path)

        parser = self.read("skills/bootstrap-repo/assets/github/scripts/issue-finalize.js")
        self.assertIn(r"^\s*Refs\s+#([1-9]\d*)\s*$", parser)
        self.assertNotRegex(parser, r"(?i)(?:delivers|completes|closes|fixes|resolves).*issueNumbers")

    def test_merge_is_not_completion_and_main_ci_is_final_acceptance(self) -> None:
        prd = self.read("docs/PRD.md")
        agents = self.read("AGENTS.md")
        finalization = self.read("skills/bootstrap-repo/references/issue-finalization.md")

        self.assertIn("Merge admits implementation to the default branch but does not itself complete", prd)
        self.assertIn("Main CI for the merged commit is the final automated acceptance gate", prd)
        self.assertIn("Completed Issues remain preserved as closed history", prd)
        self.assertIn("Merge means code entered the default branch, not that delivery is complete", agents)
        self.assertIn("PR merge != Issue completion", finalization)

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
        self.assertIn("one final delivery Pull Request", skill)

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
        self.assertIn("successful Main CI for the merged commit completes the Work Contract", skill)

    def test_review_repo_has_issue_pr_provenance_and_guard(self) -> None:
        skill = self.read("skills/review-repo/SKILL.md")
        schema = json.loads(self.read("skills/review-repo/evals/output-schema.json"))
        self.assertIn("Issue/PR provenance", skill)
        self.assertIn("six gates", skill)
        self.assertIn("issue_pr_provenance_status", schema["required"])
        self.assertIn("issue_candidates", schema["required"])
        self.assertIn("successful Main CI evidence", skill)
        self.assertIn("must not be deleted", skill)

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
            "python skills/bootstrap-repo/scripts/test_github_templates.py",
            "node skills/bootstrap-repo/scripts/test_issue_finalize.js",
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
