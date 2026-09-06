# Verification and Reporting

Use this guide to scale verification to the repair's blast radius and to report evidence without overstating confidence.

## Verification matrix

| Change surface | Minimum focused checks | Broader checks to consider |
| --- | --- | --- |
| Pure function or local module | Original reproduction, regression test, affected unit tests | Package tests; lint/type check for the package |
| Shared library or public API | Focused tests plus direct consumers and contract/serialization tests | Integration suite, compatibility tests, full type/build checks |
| State, persistence, or cache | Transition/invalidation tests and restart or reload behavior | Integration tests across lifecycle boundaries; migration/backward compatibility |
| Async or concurrency | Deterministic ordering test where possible; repeated or stress reproduction with diagnostics | Integration/end-to-end runs under realistic scheduling and cancellation |
| Dependency, runtime, CI, or platform | Clean or CI-equivalent reproduction; declared version/config/lock validation | Clean install/build on affected platforms and nearby supported versions |
| Data format or protocol | Round-trip, malformed/boundary input, and compatibility tests | Consumer/provider integration and version-skew checks |
| User-facing end-to-end path | Focused component tests and original user steps | Relevant end-to-end flow; full suite when shared infrastructure changed |

Run the narrow checks first for fast feedback. Broaden after they pass when shared code, interfaces, concurrency, state, build configuration, or multiple consumers increase blast radius. Do not run expensive unrelated suites merely for appearance, but do not omit a relevant broader check to save time.

## Regression-test quality

A useful regression test:

- fails on the pre-fix implementation for the expected contract violation;
- passes after the repair;
- asserts externally meaningful behavior or a stable invariant;
- isolates the cause closely enough to diagnose a future failure;
- does not reproduce production logic inside the assertion;
- does not depend on unstable timing, network access, or global state when a controlled substitute is possible.

If the pre-fix failure was not observed, state that explicitly. Do not describe the test as proven regression protection.

## Diff hygiene

Before completion:

1. Review `git diff` or the repository's equivalent, including generated and lock files.
2. Confirm every changed line supports the root-cause fix, regression protection, or necessary content-preserving EDD structure.
3. Check status for accidental artifacts, captured logs, snapshots, caches, formatting churn, and unrelated user files.
4. Re-run checks invalidated by any final edit.
5. Preserve pre-existing changes and identify overlap when attribution is uncertain.

## Evidence ledger

Keep enough detail to distinguish observation from inference:

| Phase | Record |
| --- | --- |
| Contract | Source paths/sections and the derived expected behavior |
| Baseline | Command or steps, inputs, environment facts, exit status, and relevant output |
| Classification | Category and the evidence that rules out nearby alternatives |
| Diagnosis | Trigger, first invalid state, violated invariant, and root cause |
| Protection | Test path/name and proof that it failed before the fix |
| Fix | Changed files and why each change is necessary |
| Verification | Each command/check and pass, fail, or not-run result |
| Residual | Untested conditions, nondeterminism, external blockers, or Source-of-Truth decision |

Use `scripts/capture_repro.py` when preserving exact command evidence materially improves auditability. It appends a structured record and does not decide whether the output proves the bug.

## Completion report

Lead with one of these accurate outcomes: **fixed and verified**, **diagnosed but not changed**, **partially verified**, or **blocked on contract/architecture**. Then state:

1. **Classification and contract:** the category and decisive PRD/EDD or other authoritative evidence.
2. **Reproduction:** the before-fix command/steps and observed failure.
3. **Root cause:** the earliest violated invariant, not only the exception.
4. **Repair:** the minimal implementation/configuration/test change and regression protection.
5. **Verification:** focused and broader checks with concrete results.
6. **Residual:** skipped checks with reasons, remaining risk, or exact decision needed.

Never use “all tests pass” when only a subset ran. Never use “fixed” when the original reproduction or essential regression test still fails.
