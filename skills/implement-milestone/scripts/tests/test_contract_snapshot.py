from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "contract_snapshot.py"
SPEC = importlib.util.spec_from_file_location("contract_snapshot", SCRIPT)
assert SPEC and SPEC.loader
contract_snapshot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(contract_snapshot)


class ContractSnapshotTests(unittest.TestCase):
    def make_repo(self, root: Path, include_edd: bool = True) -> Path:
        (root / "docs" / "milestones").mkdir(parents=True)
        (root / "AGENTS.md").write_text("# Instructions\n", encoding="utf-8")
        (root / "docs" / "PRD.md").write_text("# 产品需求\n", encoding="utf-8")
        if include_edd:
            (root / "docs" / "EDD.md").write_text("# Engineering design\n", encoding="utf-8")
        milestone = root / "docs" / "milestones" / "m1.md"
        milestone.write_text(
            "# M1\n## Scope\n- feature\n## Non-goals\n- later\n"
            "## Acceptance Criteria\n- works\n",
            encoding="utf-8",
        )
        return milestone

    def test_complete_contract_reports_fingerprints_and_sections(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            milestone = self.make_repo(root)
            payload, exit_code = contract_snapshot.build_snapshot(root, milestone)

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(len(payload["files"]), 4)
        self.assertTrue(all(item["sha256"] for item in payload["files"]))
        self.assertEqual(
            payload["milestone_sections_recognized"],
            {"scope": True, "non_goals": True, "acceptance_criteria": True},
        )

    def test_missing_required_source_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            milestone = self.make_repo(root, include_edd=False)
            payload, exit_code = contract_snapshot.build_snapshot(root, milestone)

        self.assertEqual(exit_code, 2)
        self.assertEqual(payload["status"], "error")
        self.assertTrue(any(path.endswith("EDD.md") for path in payload["missing"]))

    def test_milestone_outside_canonical_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            outside = root / "other.md"
            outside.write_text("# Not a milestone\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                contract_snapshot.resolve_milestone(root, str(outside))

    def test_utf8_bom_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            milestone = self.make_repo(root)
            milestone.write_bytes(
                b"\xef\xbb\xbf# M1\n## Scope\n## Non-goals\n## Acceptance Criteria\n"
            )
            payload, exit_code = contract_snapshot.build_snapshot(root, milestone)

        self.assertEqual(exit_code, 0)
        self.assertTrue(payload["milestone_sections_recognized"]["scope"])


if __name__ == "__main__":
    unittest.main()
