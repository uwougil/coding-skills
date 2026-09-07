# Repository health review method

## Scope before depth

Start with repository state, file inventory, root and nested `AGENTS.md`, PRD/EDD entry points, GitHub remote, Issue/PR evidence, manifests, CI, source roots, tests, and derived docs. Avoid indiscriminate full-tree reading and skip dependencies, generated binaries, caches, and build output unless evidence points there.

If the worktree is dirty, distinguish pre-existing changes from accepted `main` behavior. A health audit may inspect a requested branch or PR, but it remains independent from that task's own delivery review.

## Evidence route

For each important behavior or boundary, trace as much of this route as exists:

`PRD/EDD -> Issue Work Contract -> PR Delivery/Handoff -> accepted commit/code -> tests and CI -> derived docs`

Record missing links only when they prevent auditability, acceptance reconstruction, or safe maintenance. An old repository without historical Issue/PR metadata is not automatically defective.

## Product and architecture

Compare supported behavior and explicit non-goals against implementation. Compare dependency direction, data authority, boundaries, failure policy, compatibility, security/privacy, and deployment topology against EDD. Current code on `main` is accepted reality, but unexplained divergence is still drift.

Look across recent merged PRs for cumulative architecture changes that are harmless in isolation but violate boundaries together: cycles, duplicated authorities, new network edges, scattered composition, incompatible data paths, or growing framework surface.

## Work-contract and delivery evidence

For sampled open and closed Issues, inspect scope, acceptance criteria, validation notes, and semantic impact. For linked PRs, inspect the actual diff, tests, verification outcomes, contract-impact statement, review/CI state, and merge relationship.

High-value gaps include:

- a closed Issue whose acceptance criteria are not present in accepted code or tests;
- a merged PR with no reconstructible Work Contract for a material behavior change;
- implementation that exceeds Issue scope or silently changes PRD/EDD semantics;
- validation claims unsupported by commands, tests, or CI;
- an Issue and PR that disagree about delivered behavior.

## Verification and documentation

Inspect test quality by contract coverage, boundary realism, negative paths, and regression value—not test count. Run declared checks when safe and available. Classify command failures as product failures, environment limitations, or unrelated pre-existing failures.

Treat README, examples, schemas, generated interfaces, and operational guides as derived evidence. Prefer correcting derived artifacts to match authoritative accepted behavior; never rewrite PRD/EDD merely to rationalize code drift.

## Agent infrastructure

Inspect project-scoped skills, agents, MCP/plugin configuration, hooks, permissions, and automation only when present. Report unnecessary infrastructure when it adds broad authority, external dependencies, blocking workflow, or complexity not justified by PRD/EDD or repository operations. Ordinary host Git/GitHub operations do not require manager or orchestration skills.

## Ambiguity and escalation

When PRD, EDD, Issue, and accepted behavior disagree semantically, identify the smallest conflicting statements and the human decision needed. Such a finding is not eligible for automatic Issue creation until the semantic authority is settled. For high-confidence bounded findings, apply the six-gate review-finding check from `SKILL.md` before recommending or creating an Issue.
