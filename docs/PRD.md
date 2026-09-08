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
- Each GitHub Issue represents one independently deliverable `bug`, `feature`, or `enhancement` Work Contract. Work that cannot reasonably be delivered by one final Pull Request must be re-bounded before implementation.
- One Issue is normally completed by one final delivery Pull Request; multiple ordinary PRs do not share responsibility for completing the same Issue. The final PR carries enough repository-visible Delivery / Handoff evidence for another agent to review or continue the work and links the Issue with `Refs #N`.
- Merge admits implementation to the default branch but does not itself complete or close a Work Contract. Main CI for the merged commit is the final automated acceptance gate: success comments on and closes each still-open linked Issue with the `completed` state reason; any non-success conclusion comments and keeps the Issue open for follow-up. Completed Issues remain preserved as closed history.
- The default branch represents accepted implementation reality but does not silently supersede PRD/EDD.

## Scope

In scope are the four skill packages, directly used references/scripts/evals/assets, concise repository discovery, deterministic validation, PR-triggered CI, and default-branch CI completion feedback for linked Issues. `create-issue` may write verified GitHub Issues; bootstrap-generated GitHub automation may comment on and close linked Issues only after Main CI; the other skills retain their documented boundaries.

Out of scope are workflow engines, custom schedulers, worktree/PR/CI/merge managers, task-local-review skills, agent-specific message buses or memory services, marketplace packaging, and publishing credentials or generated evaluation artifacts.
