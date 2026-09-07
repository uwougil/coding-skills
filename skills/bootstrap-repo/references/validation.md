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
- `AGENTS.md` concisely establishes Issue-backed branch/worktree use, `Refs #N` PR delivery, reconstructible handoff evidence, green-verification merge gates, Main-CI-gated Issue completion, and human resolution for PRD/EDD changes;
- a lightweight PR template captures non-closing Issue linkage, changes, verification, and contract impact when appropriate;
- CI runs on PRs and default-branch pushes, while a separate finalizer handles only completed default-branch push CI with `contents: read`, `pull-requests: read`, and `issues: write`;
- the finalizer uses the commit-associated Pull Request API, exact standalone `Refs #N` lines, real-open-Issue checks, and idempotent comments; PR CI, direct pushes, missing references, closed Issues, and Pull Requests masquerading through the Issues API safely exit;
- no unnecessary project skill, MCP, plugin, workflow engine, scheduler, PR/CI/merge manager, or task-local-review skill was added;
- human-owned and derived artifacts are clearly distinguished.

## Git and secret review

Inspect status, staged diff, ignored files, and tracked paths. Reject real environment files, private keys, credentials, tokens, cookies, and machine-specific secrets. Never print secret values.

## Publication evidence

Record local validation results, commit identifier, remote identity, pushed branch, PR CI status, Main CI status, and finalizer status when Issue-backed delivery is enabled. If authentication, permission, or tooling is unavailable, preserve validated local state and state the exact limitation without claiming publication or Issue completion.
