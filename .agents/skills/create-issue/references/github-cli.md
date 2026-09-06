# GitHub Issue backend

The current Codex GitHub documentation describes pull-request review and cloud chat, not a general Issue-create tool exposed to this local skill. This package therefore uses the authenticated GitHub CLI (`gh`) as its narrow write backend.

## Preconditions

1. `git remote get-url origin` (or the relevant remote) resolves to the intended GitHub repository. Accept HTTPS, SSH, and GitHub Enterprise hosts; reject non-GitHub remotes instead of guessing.
2. `gh auth status --hostname <host>` succeeds. `gh` may use its existing login or `GH_TOKEN`/`GITHUB_TOKEN`; never print or request the token.
3. Read-only queries work before any mutation.

The wrapper script fails closed when `gh` is not installed, the remote cannot be parsed, authentication fails, or a command returns a non-zero status.

## Read, write, and verify commands

Run `python scripts/gh_issue.py --help` and `... <subcommand> --help` before adapting the interface. The supported operations map to these GitHub CLI capabilities:

```text
repo       resolve owner/repository from a Git remote
auth       check gh authentication for the repository host
list       list open, closed, or all Issues as JSON for duplicate search
view       fetch one Issue as JSON for post-write verification
labels     list repository labels and their names
ensure-label  create only one missing minimal type label
create     create an Issue with a title, body file, and one type label
comment    append a preservation-friendly duplicate update
edit       replace an existing Issue body only when the intent is unchanged
```

The helper never edits code, PRD/EDD, milestones, Projects, assignees, or labels other than the explicitly requested type label. Keep bodies in temporary files outside the repository when possible; do not commit them.

## Failure handling

- A missing `gh` executable: report the official install/authentication step needed; do not fall back to a guessed web action.
- An unauthenticated or unauthorized repository: report the host and command that failed; do not claim a write.
- A successful create followed by failed verification: report the returned URL/number as a partial result and stop.
- A duplicate match: do not call `create`; use `comment` by default, or `edit` only when preserving the existing body is clearly safe.

Useful official CLI references: [gh auth status](https://cli.github.com/manual/gh_auth_status), [gh issue list](https://cli.github.com/manual/gh_issue_list), [gh issue create](https://cli.github.com/manual/gh_issue_create), [gh issue edit](https://cli.github.com/manual/gh_issue_edit), and [gh issue comment](https://cli.github.com/manual/gh_issue_comment).
