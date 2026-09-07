# review-repo behavioral eval results

- Run (UTC): 2026-09-07T03:07:39+00:00
- Codex CLI: `codex-cli 0.149.1`
- Result: **9/9 passed; 0 failed; 0 blocked**
- Method: each fixture was reviewed in a separate ephemeral, read-only Codex session using `$review-repo`; structured results were graded on semantic category plus evidence paths, not prose wording.
- False-positive gates: the healthy repository must return zero findings, and semantic ambiguity must not become an auto-eligible Issue candidate.

| Case | Result | Findings | Notes |
| --- | --- | ---: | --- |
| `prd_code_conflict` | PASS | 3 | Required semantic signal and evidence found |
| `edd_dependency_violation` | PASS | 1 | Required semantic signal and evidence found |
| `closed_issue_acceptance_gap` | PASS | 1 | Required semantic signal and evidence found |
| `pr_provenance_gap` | PASS | 2 | Required semantic signal and evidence found |
| `cross_pr_architecture_drift` | PASS | 3 | Required semantic signal and evidence found |
| `stale_readme` | PASS | 1 | Required semantic signal and evidence found |
| `semantic_ambiguity` | PASS | 4 | Required semantic signal and evidence found |
| `unnecessary_agent_infra` | PASS | 2 | Required semantic signal and evidence found |
| `healthy_repo` | PASS | 0 | Required semantic signal and evidence found |

## What this eval establishes

The cases exercise PRD conflict, EDD dependency drift, closed-Issue acceptance gaps, missing PR provenance, cross-PR architecture drift, stale derived documentation, semantic ambiguity, unnecessary agent infrastructure, and a healthy repository. A passing result shows that the skill produced the expected evidence-bearing category, applied the review-to-Issue eligibility guard, and preserved the worktree.

## Limits of this eval

These fixtures are intentionally small and synthetic. Results can vary across models, reasoning settings, and future Codex releases. A BLOCKED case means the independent Codex session could not run (for example, service quota); it is neither a pass nor a skill failure. Path/category grading checks review decisions and evidence linkage, but it does not prove severity calibration on large polyglot repositories, generated code at scale, partial checkouts, or unavailable external CI/runtime dependencies. Re-run blocked cases when the service is available and rerun after material skill or model changes.
