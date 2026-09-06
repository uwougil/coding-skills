# review-repo behavioral eval results

- Run (UTC): 2026-09-06T12:55:54+00:00 (combined report from independent runs completed 2026-09-06T11:38-12:49+00:00)
- Codex CLI: `codex-cli 0.149.1`
- Result: **9/9 passed; 0 failed; 0 blocked**
- Method: each fixture was reviewed in a separate ephemeral, read-only Codex session using `$review-repo`; the first five cases ran with `gpt-5.6-sol`, and the four cases initially blocked by quota were independently rerun with `gpt-5.6-luna`. Structured results were graded on semantic category plus evidence paths, not prose wording.
- False-positive gates: the healthy repository and correct progressive-disclosure fixture must return zero findings.

| Case | Result | Findings | Notes |
| --- | --- | ---: | --- |
| `prd_code_conflict` | PASS | 1 | Required semantic signal and evidence found |
| `edd_dependency_violation` | PASS | 1 | Required semantic signal and evidence found |
| `milestone_scope_creep` | PASS | 3 | Required semantic signal and evidence found |
| `many_tests_missing_contract` | PASS | 2 | Required semantic signal and evidence found |
| `stale_readme_truth_correct` | PASS | 1 | Required semantic signal and evidence found |
| `unnecessary_agent_infra` | PASS | 2 | Required semantic signal and evidence found |
| `healthy_repo` | PASS | 0 | False-positive gate: zero findings |
| `progressive_disclosure_correct` | PASS | 0 | False-positive gate: zero findings |
| `progressive_disclosure_conflict` | PASS | 1 | Required semantic signal and evidence found |

## What this eval establishes

The cases exercise PRD conflict, EDD dependency drift, milestone scope creep, misleading test volume, stale derived documentation, unnecessary agent infrastructure, a healthy repository, and both correct and conflicting progressive disclosure. All nine independent sessions produced schema-valid reports, matched their required semantic signal (or zero findings for the two false-positive gates), and preserved the fixture worktrees.

## Limits of this eval

These fixtures are intentionally small and synthetic. Results can vary across models, reasoning settings, and future Codex releases. Path/category grading checks review decisions and evidence linkage, but it does not prove severity calibration on large polyglot repositories, generated code at scale, partial checkouts, or unavailable external CI/runtime dependencies. Rerun after material skill or model changes.
