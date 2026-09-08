# GitHub Publication

Read this reference before creating a remote repository or changing a remote.

## Resolve the Destination

Confirm or derive all non-sensitive parameters before mutation:

- GitHub host and authenticated account;
- owner or organization;
- repository name;
- public, private, or internal visibility;
- license when distribution terms matter;
- default branch and remote name;
- organization/team access or required repository policy.

Do not infer visibility. Recommend private when intent does not require public distribution, but ask the user to decide. Do not create a duplicate repository if a suitable remote already exists.

## Authenticate Safely

Prefer the GitHub tooling already installed and authenticated in the environment. With GitHub CLI, use `gh auth status --active --hostname <host>` and inspect the active account. Never use `--show-token`, echo credential-bearing environment variables, or place a token in a prompt, command line, repository, or tracked file.

If authentication is missing, stop after local validation and instruct the user to run the supported interactive authentication flow such as `gh auth login --hostname github.com`. Do not ask the user to paste a PAT into chat. Resume by rechecking authentication.

## Create and Push

Before creation, verify local status, intended staged paths, author identity, branch, and absence of tracked secrets. Make a focused initial commit. For an existing local repository, GitHub CLI supports the following shape:

```bash
gh repo create OWNER/REPO --private --source=. --remote=origin --push
```

Select exactly one resolved visibility flag; the example is not a default that bypasses clarification. If using separate Git and API commands, verify every step and avoid force pushes. Never rewrite an existing remote or its history silently.

After pushing, verify remote identity and the pushed commit with both local Git and the GitHub API/CLI, for example `git remote -v`, `git ls-remote`, and `gh repo view OWNER/REPO`.

Official references:

- https://cli.github.com/manual/gh_auth_status
- https://cli.github.com/manual/gh_repo_create

## Verify the First CI Run

Find the workflow run associated with the pushed branch or commit rather than assuming a run exists. Use `gh run list` with repository, branch, event, or commit filters as appropriate, then `gh run view` or `gh run watch <run-id> --exit-status`.

Wait for a bounded period appropriate to the repository. If a run remains queued or in progress, report the real status and a direct command or link for continuing the check; do not claim completion. If CI fails, inspect failed logs, fix in-scope defects, rerun local checks, push a focused correction, and verify the new run. Do not weaken CI merely to obtain green status.

Official reference: https://cli.github.com/manual/gh_run

## PR-first follow-up delivery

Repository birth may push the initial default branch directly. Subsequent Issue-backed or cross-agent changes should normally use an isolated branch or worktree. Each Issue is one independently deliverable Work Contract, normally completed by one final delivery Pull Request; re-boundary an outcome that cannot reasonably be delivered by one final PR instead of sharing completion responsibility across multiple ordinary PRs. The PR links its Issue with one or more exact `Refs #N` lines and summarizes changes, verification, and PRD/EDD impact. Never use `Closes`, `Fixes`, or `Resolves`: merge admits code to the default branch but does not complete the Work Contract.

Do not merge while required PR CI or task-local review is failing. After authorized merge, wait for CI on the merged commit's default-branch `push`. The separate finalizer then uses GitHub's commit-associated Pull Request API to resolve the merged PR. Main CI success comments and closes each linked open Issue with the `completed` state reason; any other conclusion comments and leaves it open. Closed Issues remain historical records and are never deleted. Routine PR creation, repair, and merge remain host-agent and GitHub responsibilities rather than separate skills.

Read [Main CI Issue finalization](issue-finalization.md) before installing or migrating this automation.
