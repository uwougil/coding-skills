---
name: implement-milestone
description: Implement an already-defined docs/milestones/*.md execution contract in an existing repository under AGENTS.md, docs/PRD.md, and docs/EDD.md constraints, including code, risk-proportionate tests, verification, diff review, and scope control. Use for executing a named milestone; do not use to invent a roadmap, draft a new PRD/EDD, or silently redesign architecture.
---

# Implement Milestone

Treat the named Milestone as the execution contract for one bounded implementation pass. Complete routine engineering work autonomously while preserving the user's product and engineering intent.

The user's explicit instructions take precedence over this skill. Do not treat a request to implement a Milestone as authorization to rewrite the product boundary or engineering design.

## Establish the contract

Identify the repository root and the exact `docs/milestones/<milestone>.md` named by the user. If the name resolves to exactly one file, proceed. Ask only when the Milestone cannot be identified unambiguously.

Before planning or editing, read the original sources in this order:

1. Root `AGENTS.md`, followed by every more-specific `AGENTS.md` that applies to files likely to change.
2. `docs/PRD.md`.
3. `docs/EDD.md` and any derived architecture, interface, or decision documents it makes authoritative for the affected area.
4. The named Milestone.
5. Current relevant implementation, tests, fixtures, schemas, and repository tooling.

Use this authority order when the sources disagree:

`PRD → EDD → Milestone → implementation`

- PRD sets the product boundary.
- EDD sets the engineering boundary.
- Milestone sets this pass's work boundary.
- Current code is evidence, not authority over the documents above.

Missing required sources are a contract problem. Report the missing source instead of inventing its contents.

When Python 3 is available, run the read-only preflight helper relative to this file:

```text
python scripts/contract_snapshot.py --repo-root <repo-root> --milestone docs/milestones/<milestone>.md
```

Use it to confirm paths and capture content fingerprints only. It never replaces reading or interpreting the original documents.

Build a working contract ledger containing:

- in-scope deliverables and acceptance criteria;
- explicit Non-goals and later-Milestone work;
- affected architecture and interfaces;
- required verification;
- unresolved material conflicts.

Keep the ledger in working notes unless the repository explicitly requires a checked-in plan. For the detailed ledger and traceability method, read [references/execution-protocol.md](references/execution-protocol.md).

## Decide whether to proceed

Proceed without asking about ordinary implementation details when a safe choice follows existing code, repository conventions, PRD, and EDD.

Pause and ask one focused question only when at least one condition holds:

- PRD or EDD has a material ambiguity with meaningfully different outcomes;
- the Milestone conflicts with PRD or EDD;
- a new requirement would change architecture or Engineering Intent;
- an external-service, security, or privacy decision requires a user choice;
- a destructive choice cannot be inferred safely.

When pausing because of this skill, identify `implement-milestone`, cite the conflicting source locations, explain the impact, and state the smallest decision needed. Do not leave routine, independent inspection unfinished before asking.

## Inspect and plan

Trace the affected execution paths, module boundaries, dependency direction, data model, interfaces, error handling, runtime constraints, security/privacy constraints, and existing tests. Inspect repository-provided build, lint, typecheck, test, and CI commands before choosing verification commands.

Research an unknown or version-sensitive technical dependency only when the repository and installed dependency sources do not resolve it. Prefer primary sources and the exact version in use. Do not research merely to justify a familiar routine choice.

Plan the smallest coherent change that satisfies every in-scope acceptance criterion. Classify each planned change as one of:

- direct Milestone deliverable;
- test, fixture, schema, configuration, or documentation required to verify/support that deliverable;
- unavoidable minimal supporting change.

Do not make an unclassified change.

## Implement without drift

Follow all EDD constraints, especially module ownership, dependency direction, runtime limits, data model, error semantics, interfaces, and security/privacy boundaries.

When code and EDD disagree, classify the mismatch before editing:

- **implementation drift:** restore the implementation to the documented design when within scope;
- **outdated derived documentation:** update the derived document from its canonical source when within scope;
- **genuine EDD design issue:** stop and report the design conflict if resolution changes EDD engineering semantics.

Never silently edit EDD to legitimize a convenient implementation.

Implement only the current Milestone Scope. Exclude explicit Non-goals, work assigned to later Milestones, opportunistic features, and unrelated large refactors. Minimal supporting changes are allowed only when the current deliverable cannot work or be verified without them; keep them narrow and explain them in the final report.

If the Milestone first appears to require a Plugin, MCP server, project-level Skill, or external integration, perform the necessity assessment in [references/execution-protocol.md](references/execution-protocol.md) before adding it. Default to existing CLI, library, or API capabilities.

## Test and verify

Every behavior change needs verification proportional to its failure risk. Select unit, integration, end-to-end, regression, fixture, and schema tests by the boundary affected, not by a coverage target. Read the test-selection table in [references/execution-protocol.md](references/execution-protocol.md) when the appropriate layer is not obvious.

Add or update tests with the implementation. Run the narrowest relevant checks first, fix failures, then run the broader applicable repository checks. Prefer fixing implementation defects. Never claim completion by deleting or skipping a valid test, weakening assertions, or lowering lint, type, build, security, or CI standards.

Distinguish failures caused by the change from unrelated pre-existing failures. Fix in-scope failures; document unrelated failures with evidence rather than hiding them.

## Apply structural progressive disclosure only when warranted

If an EDD section relevant to this Milestone has become clearly complex, is referenced by multiple modules, or has an independent lifecycle, it may be moved to one canonical derived document while EDD retains a concise summary and link.

Before doing this, read [references/progressive-disclosure.md](references/progressive-disclosure.md) and follow its move-not-copy protocol. Do not load that reference for ordinary implementations. If extraction would alter engineering semantics, treat it as an EDD design change and stop instead.

## Review the result

Inspect the complete working-tree diff, including untracked files. Preserve pre-existing user changes and separate them from this Milestone's changes.

Perform a scope-diff review before reporting completion:

- trace every changed hunk to an acceptance criterion, required verification/doc update, or justified minimal support;
- confirm every acceptance criterion has implementation and evidence;
- confirm Non-goals and later-Milestone work remain absent;
- confirm there is no unexplained architecture drift;
- inspect secrets, generated files, configuration defaults, migrations, and derived docs as applicable.

Remove or revert only changes made during this run that fail the trace. Never discard unrelated user work.

Completion requires all Milestone deliverables, checked acceptance criteria, passing applicable tests and quality gates, reviewed diff, correct secret/config handling, synchronized derived docs, and no unexplained scope or architecture drift. If any item is missing, report the work as incomplete or blocked rather than declaring success.

Use the final-report format in [references/execution-protocol.md](references/execution-protocol.md). Include implemented scope, acceptance evidence, commands and results, scope-diff outcome, architecture status, supporting changes, structural documentation changes, and any remaining blocker or pre-existing failure.
