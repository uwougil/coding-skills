# Repository Validation

Read this reference before commit or publication.

## Validate the actual stack

Derive commands from repository configuration. Run applicable setup, build/package, meaningful tests, lint/format/type/static checks, and a smoke path. CI must use reproducible setup and mirror the same core checks.

Prefer CI triggered on Pull Requests, with default-branch push checks when useful. CI execution is infrastructure, not a skill.

## Intent and delivery review

Confirm that:

- implementation does not contradict human-maintained PRD/EDD;
- repository structure follows the selected ecosystem;
- README commands were exercised;
- `AGENTS.md` concisely establishes Issue-backed branch/worktree use, PR delivery, reconstructible handoff evidence, green-verification merge gates, and human resolution for PRD/EDD changes;
- a lightweight PR template captures Issue, changes, verification, and contract impact when appropriate;
- no unnecessary project skill, MCP, plugin, workflow engine, scheduler, PR/CI/merge manager, or task-local-review skill was added;
- human-owned and derived artifacts are clearly distinguished.

## Git and secret review

Inspect status, staged diff, ignored files, and tracked paths. Reject real environment files, private keys, credentials, tokens, cookies, and machine-specific secrets. Never print secret values.

## Publication evidence

Record local validation results, commit identifier, remote identity, pushed branch, and CI run status/conclusion. If authentication, permission, or tooling is unavailable, preserve validated local state and state the exact limitation without claiming publication.
