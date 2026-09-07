# Main CI Issue Finalization

Read this reference when a target repository uses GitHub Issues as Work Contracts and Pull Requests for delivery.

## Lifecycle invariant

```text
PR merge != Issue completion
Issue completion = successful Main CI for the merged commit
```

Use exact standalone `Refs #N` lines in the PR body. They establish traceability without GitHub auto-closing the Issue. Agents must not substitute `Closes`, `Fixes`, or `Resolves`.

The full lifecycle is:

```text
Issue
→ isolated branch/worktree
→ implementation
→ PR with Refs #N
→ PR CI
→ human or otherwise authorized merge
→ Main CI on the default-branch push
→ success: completion comment + close each linked open Issue
→ non-success: failure comment + keep each linked open Issue
```

Record this invariant in the target `AGENTS.md` and in EDD or workflow documentation when those documents describe repository delivery. Keep PRD/EDD authority unchanged: this policy governs GitHub delivery state and does not redefine product or engineering intent.

## Install the bundled assets

The reusable assets are under `assets/github/`:

- `PULL_REQUEST_TEMPLATE.md` is a portable English baseline. Localize its human-facing headings and comments to the resolved collaboration language while preserving the exact `Refs #<number>` syntax and lifecycle semantics.
- `workflows/issue-finalize.yml` listens to the configured CI workflow's completed runs.
- `scripts/issue-finalize.js` contains the API and idempotency logic and is copied to `.github/scripts/issue-finalize.js`. Its default comments are English; localize the `messages` callbacks to the resolved collaboration language without changing the hidden marker or technical evidence.

For a new repository, render the files after creating the project CI workflow and determining its exact top-level `name:` value:

```bash
python <skill-dir>/scripts/render_github_templates.py \
  --root <target-repository> \
  --main-ci-workflow "<exact CI workflow name>"
```

Use `--dry-run` to inspect paths without writing. The renderer refuses to replace different existing files. For an explicitly approved migration, review the diff first and then pass `--overwrite`. After rendering, localize the PR template and finalizer comment callbacks when the repository's resolved collaboration language is not English.

## Event and API safety

Keep project tests in their existing CI workflow. The finalizer remains independent and uses `workflow_run` with `types: [completed]` for that exact workflow name. Its job-level guard requires both:

- the completed CI run's event is `push`, excluding PR CI;
- the run's `head_branch` equals `repository.default_branch`, avoiding a hardcoded branch name.

`workflow_run` jobs can receive write-capable tokens, so do not download or execute artifacts from PR CI. The bundled workflow checks out only the completed default-branch push SHA after the guard passes, and runs only the tracked finalizer script from that accepted revision.

Grant only:

```yaml
permissions:
  contents: read
  pull-requests: read
  issues: write
```

Resolve the merged PR with `repos.listPullRequestsAssociatedWithCommit`; never infer it from a commit message. Require an exact merge SHA and default-base match. Parse only standalone `Refs #N` lines, deduplicate numbers, fetch each target through the Issues API, and skip any response containing a `pull_request` field.

For an open real Issue, create a comment containing a hidden marker keyed by workflow run ID, run attempt, Issue number, and outcome. Before commenting, search existing comments for that marker. On success, close the Issue with `state_reason: completed`; on every non-success conclusion, leave it open. Already closed Issues, direct pushes without an associated merged PR, and PRs without exact references exit without mutation.

## Existing repositories

This default affects future bootstrap runs. Existing repositories gain it only through an explicit re-bootstrap or migration:

1. confirm the CI workflow runs on both Pull Requests and default-branch pushes;
2. replace auto-closing PR template text with `Refs #<number>` and the merge-versus-completion explanation;
3. render the finalizer with the exact CI workflow display name;
4. localize human-facing template prose without changing technical tokens;
5. run the template and mocked API tests, inspect the diff, and verify both a PR CI run and a post-merge Main CI/finalizer run.

Do not edit unrelated repositories or overwrite customized files without explicit migration scope.
