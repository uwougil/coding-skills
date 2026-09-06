# Semantic Review Method

Use this reference for a full repository audit or for the relevant sections in a focused audit.

## 1. Build the authority map

Classify artifacts before comparing them:

| Artifact | Primary role | Do not assume |
| --- | --- | --- |
| PRD | Product intent, user-visible constraints, non-goals | That later code silently supersedes it |
| EDD | Engineering design, boundaries, runtime, data and failure model | That every implementation divergence is an accepted redesign |
| Milestone | Current deliverables, acceptance criteria, and bounded scope | That completed checkboxes prove acceptance |
| Code/config | Actual implemented behavior and runtime structure | That implementation is intended |
| Tests/CI | Verification evidence and enforced gates | That passing tests cover the contract |
| README/examples/schemas/generated docs | Derived representation for users and tools | That stale derived text changes the source of truth |
| Structural-change log | Provenance for extracted or reorganized design content | That missing history makes either duplicate authoritative |

If sources disagree, classify the conflict as one of:

- **Implementation drift:** intent and design agree; code differs.
- **Stale derived representation:** source of truth and code agree; README/example/generated material differs.
- **Real design mismatch:** PRD and EDD disagree or the EDD cannot deliver the PRD.
- **Source-of-truth ambiguity:** multiple apparently authoritative artifacts disagree and repository evidence does not establish which was approved.

Do not resolve the last two by preference. Explain the decision the user must make.

## 2. Progressive inspection funnel

### Pass A: map

- Record repository size, languages, manifests, entry points, packages, tests, CI, docs, generated paths, and agent infrastructure.
- Inspect applicable `AGENTS.md` files and the worktree state.
- Read PRD, EDD, and only milestones plausibly connected to the reviewed implementation.
- Extract high-value nouns and contracts: actors, data, states, boundaries, external services, failure guarantees, privacy constraints, acceptance criteria, and non-goals.

### Pass B: trace

For each high-risk contract, follow this chain:

`source claim -> design mechanism -> implementation path -> test/CI evidence -> derived docs`

Prefer executable or structural evidence: call sites, imports, dependency manifests, state mutations, boundary adapters, test assertions, workflow conditions, generated schemas, and runtime configuration.

### Pass C: challenge

For each candidate finding:

- Search for an alternate implementation path, feature flag, platform variant, or nearer instruction that could explain it.
- Check whether the requirement is current, conditional, or explicitly deferred.
- Verify that the cited test actually reaches the behavior and that mocks do not replace the contract under review.
- Check whether the impact is real at the supported boundary, not merely a stylistic preference.

### Pass D: verify and stop

Run focused checks when they can distinguish competing explanations. Broaden only after a failure or unresolved risk justifies it. Stop inspecting a dimension once direct evidence and counter-evidence support a confident status.

## 3. Dimension criteria

### PRD compliance

Trace user-visible behavior and hard constraints. Pay special attention to local-first/offline promises, privacy, supported actors and workflows, data ownership, compatibility, required failure behavior, and explicit non-goals. A missing feature is a finding only when the reviewed milestone or completion claim says it should exist.

### EDD compliance

Compare intended and actual:

- runtime and deployment assumptions;
- module ownership and allowed dependency direction;
- state sources, persistence, consistency, and lifecycle;
- data flow and trust boundaries;
- public/internal interfaces and schema evolution;
- error propagation, retries, rollback, and degraded behavior;
- security/privacy controls and external services;
- dependency choices and their operational footprint.

An alternate implementation is not automatically wrong. Determine whether it preserves the design decision, represents an approved update, or creates a semantic mismatch.

### Milestone compliance

Map each deliverable and acceptance criterion to concrete implementation and verification evidence. Inspect non-goals with equal care. Flag hidden scope creep only when extra implementation adds material product surface, operational burden, privacy/security exposure, or architectural commitment—not simply because a harmless helper exists.

### Architecture drift

Derive the actual architecture from imports, calls, manifests, processes, persistent state, runtime configuration, and external endpoints. Look for forbidden dependency direction, circular coupling, abstraction leakage, duplicated responsibility, accidental global state, undocumented runtimes/services, and bypassed interfaces. Cite both the intended boundary and the actual edge.

### Test adequacy

Build a contract-to-test map. Check whether assertions prove outcomes rather than implementation trivia. Look for missing negative/failure cases, unprotected regression fixes, mocks that remove the boundary being claimed, skipped/conditional tests, and absent integration/e2e coverage only where the contract crosses a real boundary. Coverage numbers and test counts are weak supporting evidence, never the conclusion.

### Derived-document drift

Compare README, interface docs, schemas, environment examples, commands, scripts, and CI instructions with the authoritative design and observed code. Identify which representation is stale. Recommend regenerating or editing the derivative when the source of truth is clear; request a design decision when it is not.

### Agent infrastructure

Inspect project-scoped Skills, custom agents, MCP configuration, plugins, hooks, and `AGENTS.md`. For each component ask:

- What project requirement or repeated workflow needs it?
- Could an existing CLI, API, library, or short instruction do the job with less surface area?
- Are permissions, network access, and credentials bounded to the task?
- Does it duplicate another tool or contradict EDD/runtime constraints?
- Is it used and maintained, or speculative scaffolding?

Do not flag infrastructure merely for existing. Evidence should show unnecessary complexity, excessive authority, duplication, or design conflict.

### Accidental complexity

Look for speculative abstractions, premature frameworks, wrappers without policy, duplicate utilities, generic manager/service/factory layers, unused infrastructure, excessive configuration, dead code, and future-feature scaffolding. Tie every finding to PRD, EDD, milestone scope, or a demonstrated maintenance/operational consequence. Personal taste is not evidence.

## 4. Progressive-disclosure audit

When EDD content has been split into detailed documents, verify all of the following:

1. The move is an extraction, not divergent duplication.
2. EDD remains the engineering root or hub and states where authoritative details live.
3. Links resolve with correct relative paths and anchors.
4. Summaries preserve the detailed document's semantics.
5. A structural log records what moved, where, and why when the project requires such provenance.
6. Code and tests still trace back through the hub to one authoritative decision.

A healthy extraction is not fragmentation. A missing structural log is not automatically a semantic defect unless provenance is part of the project's process or the missing history leaves authority ambiguous.

## 5. Evidence quality

Prefer, in order:

1. exact path plus line range and symbol;
2. test name plus assertion or observed command result;
3. dependency edge, schema field, runtime configuration, or endpoint;
4. repository-wide search result with stated limits;
5. inference, explicitly labeled and assigned lower confidence.

Evidence must support both the actual behavior and its contrast with the expected behavior. Avoid citations to headings without the governing text.
