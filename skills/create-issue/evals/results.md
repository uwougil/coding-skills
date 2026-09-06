# `create-issue` dry-run results

Date: 2026-09-07

## Deterministic checks

- `skill-creator` `quick_validate.py`: passed (UTF-8 mode).
- Repository `scripts/validate_skills.py`: passed; five packages and JSON assets validated.
- Existing focused helper tests: 5 + 4 tests passed.
- `gh_issue.py --help`: passed.
- `test_gh_issue.py`: 5 wrapper tests passed (remote parsing, JSON list, create command, body-file guard).
- Remote parser smoke test (`git@github.com:octo/example.git`): passed.
- Live GitHub create/update: not run. This environment has no `gh` executable and no live Issue mutation is appropriate for a dry-run.

## Behavioral cases

| Case | Result | Evidence in skill contract |
| --- | --- | --- |
| A — Simple feature | Pass | `feature` classification and one-issue default. |
| B — Enhancement | Pass | Explicit “already possible → enhancement” rule. |
| C — Bug | Pass | Existing-contract classification and conditional `Reproduction`. |
| D — Duplicate | Pass | Open + closed semantic search; no duplicate; comment/update path. |
| E — Multiple work items | Pass | Split proposal requires explicit confirmation before multi-write. |
| F — PRD conflict | Pass | Read-only PRD gate and write hard stop. |
| G — EDD conflict | Pass | Read-only EDD gate and no silent architecture redefinition. |
| H — Rejected AI suggestion | Pass | Accepted/rejected intent ledger excludes unaccepted suggestions. |
| I — Over-splitting | Pass | Implementation steps are explicitly not Issues. |
| J — No coding | Pass | Stop after verified Issue and explicit no-code boundary. |

These are protocol dry-runs, not proof of GitHub permissions. A real run must still verify the target remote, `gh auth status`, duplicate results, and post-write `issue view`.
