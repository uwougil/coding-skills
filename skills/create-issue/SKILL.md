---
name: create-issue
description: "Compile settled human intent or a high-confidence repository-review finding into a concise, repository-aware GitHub Issue, with duplicate detection and PRD/EDD conflict guards. Use for real Issue intake; do not use for implementation or intent-document editing."
metadata:
  short-description: "Compile accepted work into guarded GitHub Issues"
---

# Create Issue

Create a verified GitHub Issue as one independently deliverable and independently understandable Work Contract. This skill owns intake, not implementation, planning orchestration, PRD/EDD editing, or Pull Request delivery.

## Authority and hard stops

- Read but never modify applicable `AGENTS.md`, `docs/PRD.md`, and `docs/EDD.md`.
- PRD is human-maintained Product Intent; EDD is human-maintained Engineering Intent. An Issue may refine accepted work but cannot silently redefine either contract.
- The top-level type taxonomy is exactly `bug`, `feature`, or `enhancement`. Do not introduce other top-level types.
- Do not modify source, tests, CI, configuration, PRD, or EDD. Stop after a verified Issue create/update/comment.
- Never write before target repository, authentication, source-mode eligibility, and open-plus-closed duplicate search are verified.

## Select one source mode

### `human-settled-intent`

Use when a human asks to materialize an accepted feature, enhancement, or bug. Read the full supplied conversation and separate:

- latest user-accepted decisions;
- rejected, superseded, exploratory, quoted, or AI-suggested ideas;
- observable outcome, constraints, non-goals, and bug reproduction evidence.

Only settled human intent becomes a Work Contract. Ask one focused question only when an unresolved choice materially changes product behavior, engineering semantics, security/privacy, destructive behavior, acceptance criteria, or repository identity.

### `review-finding`

Use when an independent `review-repo` automation supplies a material finding. Human repetition is not required, but autonomous Issue creation is allowed only when all are present:

1. a specific authoritative repository expectation or clearly evidenced maintenance invariant;
2. direct repository evidence of actual behavior or structure;
3. a plausible material consequence;
4. a bounded actionable remedy;
5. semantic duplicate search across open and closed Issues;
6. high confidence that a Work Contract is more useful than reporting uncertainty.

If the finding is uncertain, would change PRD/EDD semantics, or exposes a source-of-truth conflict, report and escalate it to the human; do not create an Issue that chooses the design. When helpful, validate a structured finding with `scripts/gh_issue.py check-review-finding --finding-file ...` before any write.

## Inspect and classify

Read scoped repository instructions and relevant PRD/EDD sections, then only the source, tests, history, Issues, and PRs needed to establish the contract. Implementation is evidence, not authority.

Classify exactly one type:

- `bug`: promised behavior fails, regresses, crashes, or is incorrect;
- `feature`: the capability is absent or previously impossible;
- `enhancement`: an existing capability is improved, extended, or optimized.

One independently deliverable outcome normally becomes one Issue and is expected to be completed by one final delivery Pull Request. If the outcome cannot reasonably be delivered by one final PR, revisit the Issue boundary before writing; do not create a contract whose completion responsibility must be shared across multiple ordinary PRs. If settled intent contains multiple independent outcomes, show a short split proposal and wait for human confirmation before multiple writes. Never split implementation steps into micro-Issues or design the implementation PR while composing the contract.

## Search duplicates

Resolve the Git remote, verify `gh` authentication, then search both open and closed Issues using distinctive behavior terms, identifiers, and errors. Compare semantics:

- equivalent: do not create; preserve useful context with an additive comment, or edit only when a clean correction keeps the same intent;
- overlapping but distinct: keep separate and state the boundary;
- no meaningful match: continue.

Read [the GitHub backend reference](references/github-cli.md) before querying or writing.

## Compose the Work Contract

Resolve the collaboration language before drafting the title or body: explicit repository or user instruction, scoped `AGENTS.md` policy, dominant language of human-maintained PRD/EDD, then the current settled human request. Explicit instruction wins over an old template, history, code comments, or technical source. Use the resolved language for human prose, including `review-finding` output, while preserving technical terms, identifiers, errors, commands, paths, URLs, API names, and GitHub numbers verbatim. Never hardcode Chinese; English and other repository languages remain valid. Use concise repository-appropriate prose. Default body:

```markdown
## Summary

<observable problem or outcome>

## Acceptance Criteria

- [ ] <observable, testable result>
- [ ] <important compatibility or constraint result>
```

Add `Reproduction` for useful bug evidence, `Review Evidence` for autonomous findings, and `Non-goals` only when they prevent likely scope creep. Do not prescribe speculative file lists, classes, libraries, pseudo-code, or mini-EDD architecture.

Apply exactly one type label. Assess parallel scheduling as a temporary hint from affected area, known dependencies, shared state, schemas/migrations, global configuration, public interfaces, and overlap with known work. When repository conventions support it, use minimal metadata such as `parallel:candidate`, `parallel:risky`, `parallel:blocked`, `depends-on:<issue>`, or `area:<subsystem>`. These are not Issue types, and the builder must recalculate safety from current state.

## Write and verify

Use `scripts/gh_issue.py` or equivalent authenticated `gh` commands. Never accept or expose tokens. Verify the final Issue with `issue view` and report repository, number, URL, operation, type, and scheduling hints. If a write partially succeeds, report the exact partial state and stop. Do not proceed into implementation.

## Supporting resources

- Read [references/github-cli.md](references/github-cli.md) for remote, auth, duplicate, label, finding-gate, and write/verify behavior.
- Run `python scripts/gh_issue.py --help` before adapting the wrapper.
- Read [evals/README.md](evals/README.md) when evaluating human and review-finding intake behavior.
