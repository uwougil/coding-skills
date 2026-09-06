# Execution protocol

Use this reference while building the contract ledger, selecting verification, assessing new agent infrastructure, reviewing the diff, or writing the final report.

## Contract ledger

Maintain a compact working ledger before editing:

| Item | Source location | Intended implementation | Evidence | Status |
|---|---|---|---|---|
| Deliverable or acceptance criterion | Milestone line/heading | Files or behavior expected to change | Planned test/check | pending/done/blocked |

Record explicit Non-goals and later-Milestone items in a separate exclusion list. Record EDD constraints that govern the affected modules even when the Milestone does not repeat them. Do not check this ledger into the repository unless project instructions require it.

Convert vague implementation language into observable behavior only when the meaning follows unambiguously from PRD, EDD, code conventions, or tests. Otherwise, treat materially different interpretations as a contract ambiguity.

## Repository inspection

Inspect enough context to understand the complete affected path:

1. Find the repository's documented commands and CI configuration.
2. Trace callers, callees, data ownership, error paths, public interfaces, persistence, and external boundaries.
3. Locate neighboring tests and fixtures before choosing a new test location.
4. Check the working tree before editing so user changes are not mistaken for Milestone work.
5. Identify linked derived documents whose canonical content is affected.

Avoid repository-wide exploration after the affected boundaries are known unless evidence points outside them.

## Architecture mismatch classification

Use these tests when EDD and code disagree:

### Implementation drift

The EDD is internally coherent, current requirements still depend on it, and code departed from it without an authoritative design decision. Restore code to EDD when that repair is necessary for the current Milestone and does not introduce unrelated refactoring.

### Outdated derived documentation

A canonical EDD statement or authoritative interface/design document has changed, but a lower-authority summary, generated reference, diagram, or example was not synchronized. Update the derived material and links without changing Engineering Intent.

### Genuine EDD design issue

The Milestone cannot be implemented safely or coherently without changing module ownership, dependency direction, runtime model, data model, interface semantics, error policy, or security/privacy constraints. Stop before making the semantic design change. Report:

- the conflicting source locations;
- why both cannot be satisfied;
- impact on the current Milestone;
- the smallest design decision or EDD amendment needed;
- any safe work already completed that does not prejudge the decision.

Do not relabel a design change as drift repair or documentation cleanup.

## Risk-proportionate test selection

Choose all layers justified by the changed behavior:

| Change characteristic | Evidence normally required |
|---|---|
| Pure local logic with stable collaborators | Focused unit test, including material edge/error cases |
| Previously failing behavior | Regression test that fails before and passes after the fix |
| Interaction across real module/process/storage/network boundaries | Integration test using the closest practical real boundary |
| User-critical flow spanning multiple components | End-to-end test when the repository has a viable E2E layer |
| Parser, serializer, schema, migration, or public payload | Representative fixtures plus schema/compatibility validation |
| Configuration or secret handling | Default/invalid-path tests and a check that no secret enters source, logs, fixtures, or diff |
| Documentation-only structural move | Link validation and a semantic/content-preservation review |

One test may cover several risks. Do not add redundant layers solely to increase test counts. Conversely, a unit mock is not sufficient evidence for a new integration boundary.

Run checks in this order when applicable:

1. the new or changed test directly exercising the behavior;
2. the affected module/package suite;
3. lint, formatting, static analysis, typecheck, schema or migration checks;
4. broader repository tests and build;
5. end-to-end or expensive validation justified by risk.

Record the exact commands and whether they passed, failed, or could not run. Do not report a check as passed when it was not executed.

## Agent-infrastructure necessity assessment

Before first introducing a Plugin, MCP server, project-level Skill, or external integration, answer in working notes:

1. Which current acceptance criterion requires it?
2. Why existing repository code, CLI, library, or API facilities are insufficient.
3. What new lifecycle, operational, security, privacy, credential, and maintenance burden it creates.
4. Whether a smaller local adapter or ordinary dependency satisfies the same need.
5. Whether PRD and EDD authorize the new boundary.

Default to not introducing the infrastructure. If an external-service, security, privacy, credential, or architecture decision remains, ask the user before adding it.

## Scope-diff review

Review the final diff hunk by hunk. Classify each hunk as:

- `AC:<id or short name>` — directly satisfies an acceptance criterion;
- `VERIFY:<criterion>` — test, fixture, schema, or validation evidence;
- `DOC:<canonical source>` — required synchronization or content-preserving extraction;
- `SUPPORT:<reason>` — unavoidable minimal support.

The labels may remain in working notes; do not insert them into source code. Any unclassifiable hunk is scope creep and should be removed if it was created during this run. Re-check explicit Non-goals and inspect later Milestone files so TODOs, convenient helpers, or generalized APIs do not pre-implement future work.

For every `SUPPORT` hunk, confirm that removing it would make an in-scope deliverable fail or become unverifiable. Convenience alone is not sufficient.

## Completion gate

Do not mark the Milestone complete until all applicable checks are true:

- all deliverables are implemented;
- each acceptance criterion has observable evidence;
- targeted tests pass;
- broader applicable tests and lint/type/build/schema checks pass;
- the scope-diff review found no unexplained change;
- architecture is aligned or every drift repair is explained;
- secrets/configuration, errors, migrations, and compatibility are correct;
- canonical and derived documentation are synchronized;
- the complete working tree and diff were reviewed.

An unrelated pre-existing failure does not authorize hiding it. State the exact failure and whether it prevents confidence in the Milestone.

## Final report

Lead with `complete`, `incomplete`, or `blocked`. Then report only evidence that helps the user assess the result:

1. **Implemented scope:** deliverables and any minimal supporting changes.
2. **Acceptance evidence:** criterion-to-test/check mapping.
3. **Verification:** exact commands with pass/fail/not-run status.
4. **Scope and architecture:** Non-goals/later work excluded, scope-diff result, drift classification.
5. **Documentation structure:** each automatic extraction, source, destination, links updated, and structural-log location; say `none` when absent.
6. **Remaining issues:** blockers or pre-existing failures, with impact.

Do not claim a clean working tree unless verified. Distinguish pre-existing user changes from changes made for the Milestone.
