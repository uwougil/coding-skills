# Product Requirements

## Product intent

Provide a portable four-skill protocol library for repository engineering with strong general coding agents and standard Git/GitHub artifacts as shared state.

The shipped skills are exactly:

- `bootstrap-repo`
- `create-issue`
- `fix-bug`
- `review-repo`

## User outcomes

Users can establish a maintainable repository, turn settled work into GitHub Issues, execute bugs under a rigorous debugging protocol, and periodically audit repository-wide semantic health. Different builders and reviewers must be able to collaborate without shared private conversations or proprietary memory.

## Durable contracts

- Humans maintain `docs/PRD.md` as Product Intent and `docs/EDD.md` as Engineering Intent.
- GitHub Issues represent independently understandable `bug`, `feature`, or `enhancement` Work Contracts.
- Pull Requests represent Delivery / Handoff Contracts, carrying enough repository-visible evidence for another agent to review or continue the work.
- The default branch represents accepted implementation reality but does not silently supersede PRD/EDD.

## Scope

In scope are the four skill packages, directly used references/scripts/evals, concise repository discovery, deterministic validation, and PR-triggered CI. `create-issue` may write verified GitHub Issues; the other skills retain their documented boundaries.

Out of scope are workflow engines, custom schedulers, worktree/PR/CI/merge managers, task-local-review skills, agent-specific message buses or memory services, marketplace packaging, and publishing credentials or generated evaluation artifacts.
