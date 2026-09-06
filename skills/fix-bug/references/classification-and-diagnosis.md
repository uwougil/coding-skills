# Classification and Diagnosis

Use this guide when classification is uncertain, when evidence points outside ordinary implementation code, when history matters, or when the proposed repair may change architecture semantics.

## Evidence standard

A classification is a working hypothesis until the baseline reproduction and contract evidence support it. Record contrary evidence and reclassify instead of forcing the first theory.

| Category | Evidence needed | Authorized repair path | Stop condition |
| --- | --- | --- | --- |
| Implementation bug | An authoritative PRD/EDD rule plus a faithful reproduction showing code divergence | Add or identify a failing regression test, then correct the implementation | The contract is missing or conflicting |
| Regression | Evidence of previously correct behavior from history, releases, tests, or a known-good revision, plus the current failure | Find the likely introduction point, protect the old contract, and minimally repair the regression | Restoring old behavior conflicts with the current contract |
| Spec ambiguity | Relevant authoritative sources omit the disputed case or disagree | Report the exact unresolved decision and name the Source of Truth that must decide it | Any patch would invent product or architecture semantics |
| Environment/dependency bug | Failure correlates with runtime, lockfile, toolchain, CI, configuration, platform, external service, or integration boundary | Correct the narrow setup, constraint, compatibility layer, configuration, or declared dependency cause | A proposed business-code workaround merely masks an unsupported environment |
| Test bug | Independent contract evidence and an implementation-level observation show the assertion, fixture, mock, ordering, or harness is wrong | Correct the test while preserving or strengthening its contract assertion | The only evidence is that the test fails or that changing it makes CI green |

## Contract precedence

Apply the repository's explicit authority rules when present. Otherwise, treat accepted PRD behavior as product intent and the EDD as its architectural realization; neither a test nor the current implementation silently overrides them. A Milestone can narrow delivery scope but should not silently redefine the product contract.

When sources conflict, quote or point to the smallest relevant passages and ask one concrete question. Preserve work already supported by undisputed contract sections, but do not implement the disputed behavior.

## Regression history

Use history proportionally:

1. Identify the last known-good behavior or revision when evidence exists.
2. Inspect the smallest relevant log, blame range, or diff.
3. Separate the change that exposed the bug from the change that created the invalid state.
4. Do not revert an entire change when a smaller correction preserves its intended behavior.

If the repository has no useful history, say so and classify from the available contract and behavior evidence.

## Root-cause chain

Describe the causal chain in this order:

1. **Trigger:** the input, event, state, or environment condition.
2. **Propagation:** the relevant calls, transitions, queues, serialization steps, or integration boundaries.
3. **First invalid state:** the earliest point where an invariant becomes false.
4. **Root cause:** the missing or incorrect rule that permits that invalid state.
5. **Symptom:** the user-visible error, exception, bad output, hang, or failing assertion.

Use a counterfactual check: if only the proposed line changed, would every faithful version of the reproduction stop violating the contract? If it only suppresses the final symptom, continue diagnosing.

## Failure dimensions

Inspect only dimensions relevant to the evidence, but do not overlook:

- input shape, validation, normalization, and trust boundaries;
- state-machine transitions, retries, idempotency, and partial completion;
- async scheduling, races, cancellation, timeouts, and resource lifetime;
- empty, zero, maximum, equality, overflow, locale, and time boundaries;
- serialization versions, encoding, precision, and schema compatibility;
- dependency versions, lockfiles, runtime/toolchain constraints, and API drift;
- environment variables, generated config, CI parity, filesystem paths, and platform behavior;
- stale caches, migrations, persisted state, and invalidation;
- caller/callee assumptions and interface mismatches.

## Architecture conflict

An architecture conflict exists when the smallest correct repair changes an EDD semantic decision rather than restoring it. Stop the disputed implementation and report:

- the reproduction and root cause already proven;
- the current EDD rule and why it cannot satisfy the PRD or observed requirement;
- the smallest architecture decision needed;
- affected components and verification that would follow the decision.

Do not disguise a semantic redesign as refactoring.

## Content-preserving EDD disclosure

When an EDD section is too large or entangled to navigate safely, restructure only when doing so is genuinely necessary:

1. Move content without changing meaning.
2. Keep stable anchors or update every inbound link.
3. Leave a short routing summary at the original entry point.
4. Record moved headings, old/new locations, and link changes in a structural log.
5. Keep semantic proposals separate and unimplemented until approved.
