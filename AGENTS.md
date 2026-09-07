# Repository Instructions

## Contracts

- `docs/PRD.md` and `docs/EDD.md` are human-maintained Product Intent and Engineering Intent. Never change their semantics without explicit human resolution.
- GitHub Issues are Work Contracts. Issue-backed changes should normally use an isolated branch or worktree and be delivered through a Pull Request.
- A Pull Request is the repository-visible Delivery / Handoff Contract. Another agent must be able to reconstruct the work from PRD/EDD, the linked Issue when present, commits, PR description and diff, tests, and CI without private conversation state.
- Do not merge Issue-backed work while required verification is failing. The default branch is accepted implementation reality, not authority to silently override PRD/EDD.

## Repository maintenance

- Keep exactly `bootstrap-repo`, `create-issue`, `fix-bug`, and `review-repo` under `skills/`; do not add orchestration, merge, CI, or task-local-review skills.
- `.agents/skills/create-issue/` is a discovery mirror of `skills/create-issue/`; keep tracked files byte-for-byte synchronized.
- Keep skill entrypoints, references, scripts, eval manifests, root docs, validator, and CI consistent.
- Run every deterministic command in `README.md` before delivery. Preserve unrelated work and never commit credentials, caches, generated workspaces, or raw model logs.
