# GitHub Issue backend

Use the authenticated GitHub CLI as the narrow read/write backend. Standard GitHub Issues are the portable Work Contract surface.

## Preconditions

1. Resolve the intended GitHub remote; accept HTTPS/SSH GitHub remotes and fail closed on unknown hosts.
2. Verify `gh auth status --hostname <host>` without printing credentials.
3. Select `human-settled-intent` or `review-finding` and satisfy its gate.
4. Search semantically across both open and closed Issues before mutation.

## Wrapper operations

Run `python scripts/gh_issue.py --help` and the selected subcommand help.

```text
repo                  resolve owner/repository
auth                  verify authentication
list                  search open, closed, or all Issues
view                  verify one Issue
labels                inspect conventions
ensure-label          create one safe missing label
check-review-finding  fail closed on incomplete/ambiguous review evidence
create                create one Issue with one type and optional existing metadata labels
comment               append useful duplicate context
edit                  replace a body only when intent is unchanged
```

`check-review-finding` validates structure; it does not replace the agent's inspection of repository evidence or live duplicate results. Eligible review input must state expectation, direct evidence, consequence, bounded remedy, high confidence, no required PRD/EDD semantic change, and completed open-plus-closed duplicate search with no equivalent Issue.

Type labels are exactly `bug`, `feature`, or `enhancement`. Scheduling labels are optional hints and must use the repository's existing conventions; do not create dynamic label taxonomies speculatively.

Keep Issue bodies in temporary files outside the repository when practical. The helper never edits code, PRD/EDD, Projects, assignees, or PRs and never accepts tokens as arguments.

## Failure handling

- Missing CLI/auth/repository: report the exact failure; do not switch to guessed web mutation.
- Equivalent Issue: do not create a duplicate.
- Ineligible review finding or semantic ambiguity: report/escalate; do not write.
- Successful write followed by failed verification: report the returned URL/number as partial and stop.

Official references: [gh auth status](https://cli.github.com/manual/gh_auth_status), [gh issue list](https://cli.github.com/manual/gh_issue_list), [gh issue create](https://cli.github.com/manual/gh_issue_create), [gh issue edit](https://cli.github.com/manual/gh_issue_edit), and [gh issue comment](https://cli.github.com/manual/gh_issue_comment).
