---
name: fix-bug
description: "Execute bug work with an evidence-first, Issue-backed protocol: establish the contract, reproduce, diagnose root cause, add regression protection, make the minimal correct fix, and produce PR-ready verification evidence. Automatically adopt this protocol when a linked Issue is typed bug. Do not use for planned features or speculative refactors."
metadata:
  short-description: "Evidence-first bug repair"
---

# Fix Bug

Use an evidence-first repair protocol. The user's instructions take precedence over this skill. Preserve the user's requested scope: a request to diagnose, review, or explain does not authorize edits; a request to fix authorizes the affected code, tests, and ordinary verification, but not unrelated redesign.

Automatically adopt this protocol when the active Work Contract is a GitHub Issue whose exact type is `bug`, even when the user does not name the skill. For an untyped report, classify it first; do not relabel feature work as a bug to bypass its acceptance contract.

Follow this sequence and do not patch before the first four gates are satisfied:

> reproduce -> prove -> diagnose -> regression test -> minimal fix -> verify -> broader regression check

If a gate is infeasible, state why, use the strongest available substitute, and preserve the limitation in the final report. Never silently skip a gate.

## Scope boundary

This skill owns debugging semantics. It does not own task scheduling, branch or worktree orchestration, generic feature implementation, merge coordination, or repository-wide review. The host coding agent may perform ordinary Git/GitHub and Pull Request operations using the evidence this protocol produces.

## 1. Establish the contract and local context

Before changing code:

1. Discover and read every `AGENTS.md` whose scope covers the affected files.
2. Read the linked Issue first when one exists. Treat its accepted scope, acceptance criteria, and validation notes as the Work Contract; then locate the relevant PRD and EDD sections that govern product and architecture semantics.
3. Read the affected source and tests, along with logs, stack trace, recent linked PR context, and user reproduction steps that are available.
4. Inspect repository status and preserve pre-existing user changes.
5. State the expected behavior, observed behavior, and the contract evidence that distinguishes them.

Do not infer a product or architecture contract from a failing test alone.

## 2. Classify the bug

Choose the best-supported category, and revise it if later evidence disproves it:

- **Implementation bug:** code violates a clear existing PRD/EDD contract.
- **Regression:** previously correct behavior was broken by a later change. Locate the likely introduction point when history is available.
- **Spec ambiguity:** the authoritative sources conflict or do not define the disputed behavior. Do not invent the missing rule; identify the Source of Truth and the exact clarification needed.
- **Environment/dependency bug:** runtime, dependency, build, CI, configuration, platform, or external integration causes the failure. Repair that cause instead of hiding it in business logic.
- **Test bug:** the test contradicts the proven contract. Prove that contradiction independently before modifying the test.

Read [classification-and-diagnosis.md](references/classification-and-diagnosis.md) whenever the category is uncertain, the suspected problem is a test/environment/spec issue, history matters, or the proposed fix changes EDD semantics.

## 3. Reproduce and prove the baseline

Build the smallest faithful reproduction and run it against the unchanged implementation. Record the exact command or steps, inputs, relevant environment, exit status, and the failure that proves the reported behavior exists.

For a stable, important implementation bug or regression, add or identify a permanent regression test before changing production code. Run it and confirm that it fails for the expected reason. Prefer the existing test system and nearest relevant test file. Use an existing `tests/regression/` directory when appropriate; create one only when regression cases already form a useful independent category.

Do not add a duplicate test when an existing test already reproduces the exact contract violation. For a suspected test bug, preserve the original failure and first prove that the assertion, fixture, or harness conflicts with the contract.

If deterministic automation is impossible, explain the instability and use the most reliable substitute: a controlled integration reproduction, targeted instrumentation, a recorded fixture, repeated stress execution, or explicit manual steps. Do not claim the bug is reproduced or fixed when the evidence does not show it.

Use the repository's declared runner and dependency environment first. Try only a small number of safe, project-relevant alternatives when a launcher is unavailable; do not install, upgrade, or broadly probe unrelated runtimes just to force a green result. If the environment remains unavailable, stop runtime investigation, preserve the exact limitation, and use a source-level or controlled substitute only when it genuinely exercises the reported contract.

For complex or disputed failures, optionally capture command evidence with `scripts/capture_repro.py`; read its `--help` before use. Store transient logs outside tracked source unless the project defines a location or the user requests an audit artifact.

## 4. Diagnose root cause

Trace backward from the symptom to the first invalid state or violated invariant. Separate trigger, propagation path, root cause, and visible symptom. Check the relevant failure dimensions: input validation, state transitions, concurrency, async ordering, boundaries, serialization, external dependencies, configuration, platform differences, stale cache/state, and interface mismatch.

Before editing, explain why the proposed change addresses the cause and not merely the final exception. A catch-all, retry, fallback, or guard is valid only when the contract makes it part of the correct boundary behavior.

## 5. Add regression protection and make the minimal fix

Protect stable, important bugs with a test that observes the contract and that failed before the fix. Then make the smallest coherent change that resolves the root cause.

Avoid unrelated refactors, premature abstractions, scope expansion, broad dependency upgrades, error suppression, catch-all exception handling, skipped tests, weakened assertions, and disabled lint/type checks. Change tests only when adding valid protection or after proving a test bug. For dependency/environment bugs, prefer the narrow configuration, lockfile, toolchain, or integration correction that restores the declared environment.

If a correct fix must change EDD semantic design, stop that portion of implementation and report an architecture conflict with the decision required. Continue only with nondisputed diagnostics or changes.

If investigation exposes an EDD section that genuinely requires structural splitting, apply only content-preserving progressive disclosure: preserve semantics, anchors, and links; add routing and a structural log; report it separately from the repair. Do not redesign the EDD under a bug-fix label.

## 6. Verify from focused to broad

After the patch:

1. Re-run the original reproduction.
2. Re-run the new or existing regression test.
3. Run affected unit tests.
4. Run relevant integration tests.
5. Decide from blast radius whether the full suite or end-to-end tests are warranted.
6. Run applicable lint, type, and build checks.
7. Inspect the final diff and status for minimality and unrelated changes.
8. Assemble final-delivery-PR-ready evidence: linked Issue, before/after reproduction, regression test, commands and outcomes, scope boundary, and any PRD/EDD impact. One bug Issue is normally completed by this one final delivery PR; if the repair cannot reasonably preserve that independently deliverable boundary, stop and return to Issue intake instead of sharing completion responsibility across multiple ordinary PRs. Use the repository's resolved collaboration language for human-facing handoff prose; preserve commands, errors, identifiers, paths, URLs, API names, and GitHub numbers verbatim.

Read [verification-and-reporting.md](references/verification-and-reporting.md) for cross-component, async/concurrency, dependency/platform, data-format, or otherwise high-blast-radius fixes. Report every material check as passed, failed, or not run with a reason; distinguish unrelated pre-existing failures without hiding them.

## 7. Report the evidence

Lead with the outcome, then include:

- classification and contract evidence;
- reproduction and pre-fix proof;
- root cause;
- regression protection and minimal fix;
- verification commands/results, including broader checks;
- the Issue acceptance criteria satisfied and the final delivery PR handoff evidence;
- the post-merge acceptance rule: merge only admits code to the default branch, while successful Main CI for the merged commit completes the Work Contract;
- residual risks, limitations, or required Source-of-Truth decision.

Do not call the issue fixed if the original reproduction or essential regression test is still failing.
