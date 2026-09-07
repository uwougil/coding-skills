---
name: review-repo
description: "Audit repository health independently across PRD/EDD intent, GitHub Issue work contracts, PR delivery evidence, accepted code on main, tests, CI, derived docs, and agent infrastructure. Use for repository health checks, architecture drift across changes, closed-Issue acceptance gaps, provenance gaps, test adequacy, or documentation drift. Not for task-local diff review or feature implementation."
metadata:
  short-description: "Issue/PR-aware repository health audit"
---

# Review Repository

Perform an independent, evidence-backed repository health audit. The source tree and human-owned PRD/EDD stay read-only. This is not the final review step of another skill and does not approve or merge a PR.

## Authority and provenance

Interpret evidence in this order:

1. PRD defines accepted product behavior; EDD defines accepted architecture.
2. An Issue is a bounded Work Contract. It may narrow work but cannot silently change PRD/EDD semantics.
3. A PR is Delivery/Handoff evidence: scope, changes, validation, contract impact, review, and merge decision.
4. `main` is accepted implementation reality, not an automatic override of PRD/EDD.
5. Tests, CI, and derived docs are evidence about those contracts, not independent authorities.

When semantic authorities conflict, report the ambiguity and request a human decision. Do not edit PRD/EDD, source, tests, or docs during a review.

## Review loop

1. Resolve repository root, current revision, worktree status, remote, and review scope.
2. Read all applicable `AGENTS.md` files.
3. Build a bounded inventory with `scripts/repo_inventory.py` when it helps.
4. Read relevant PRD/EDD sections, open and recently closed Issues, recent merged PRs, source, tests, CI, and derived docs. Use repository-visible Issue/PR artifacts when remote metadata is unavailable.
5. Reconstruct important paths as `PRD/EDD -> Issue -> PR -> accepted code -> tests/CI/docs`.
6. Inspect architecture drift across multiple accepted PRs, not only the latest diff.
7. Run safe read-only verification when available; record unavailable evidence precisely.
8. Report only substantive findings that pass the threshold below.

Classify a closed-Issue acceptance failure as `Work Contract Compliance` even when it also violates PRD/EDD; use the status summaries to record the wider contract impact without duplicating the finding.

Read [review-method.md](references/review-method.md) for progressive inspection and [report-contract.md](references/report-contract.md) before producing the final report.

## Finding threshold

Report a finding only when all are present:

- an authoritative expectation or explicit provenance requirement;
- direct repository evidence with tight paths, lines, symbols, Issue/PR identifiers, or command output;
- a material product, architecture, correctness, operational, verification, or maintenance consequence;
- a bounded remedy.

Do not report preferences, hypothetical risks without a credible path, missing optional artifacts, or duplicate symptoms of one root cause.

## Review-to-Issue escalation

A review finding may be offered to `create-issue` in `review-finding` mode only when all six gates pass:

1. direct evidence is sufficient;
2. the consequence is material;
3. the remedy is bounded;
4. confidence is high;
5. open and closed Issue search found no equivalent;
6. the remedy does not require an unapproved PRD/EDD semantic change.

If the invocation authorizes repository-health automation, invoke `create-issue` only for eligible findings and include evidence, contract impact, and validation notes. Otherwise return eligible candidates without mutating GitHub. Never create an Issue for ambiguity, low-confidence suspicion, style preference, or a duplicate. Source and documentation remain read-only in either case.

## Output

Lead with findings ordered by severity. Then summarize PRD status, EDD status, Issue/PR provenance status, test confidence, architecture drift, derived-doc status, agent-infrastructure fitness, eligible Issue candidates, and recommended next actions. Write this repository-facing report in the resolved collaboration language from scoped policy, and preserve technical evidence verbatim. State explicitly when no substantive findings exist.
