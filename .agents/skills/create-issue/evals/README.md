# create-issue evaluation matrix

These are behavior contracts for dry-runs. They are intentionally side-effect free: use a fixture repository and a mocked `gh` executable, or inspect the model's proposed action before allowing a real write.

| Case | Input | Expected behavior |
| --- | --- | --- |
| A | “只支持 YouTube，新增 Bilibili” | One `feature` Issue; concise behavior-based acceptance criteria. |
| B | Existing SRT export, add ASS | One `enhancement` Issue, not `feature`. |
| C | Existing input crashes | One `bug` Issue with `Reproduction` only when useful. |
| D | Semantically equivalent existing open/closed Issue | No duplicate; append useful context or safely update the existing Issue, then verify. |
| E | Three independent outcomes | Show numbered split proposal and wait for confirmation before any multi-Issue write. |
| F | Request contradicts PRD | No GitHub write; name the PRD conflict and request source-of-truth update. |
| G | Request contradicts EDD architecture | No silent architecture redefinition or Issue write. |
| H | AI suggests Redis; user rejects it | Redis must not appear in title, body, criteria, labels, or commands. |
| I | One normal feature | Do not produce implementation-level micro-Issues. |
| J | Issue write succeeds | Stop after verified Issue; no source/test/PRD/EDD/milestone edits. |

## Dry-run result

The first review should check each row against the `SKILL.md` gates and the final diff. A live GitHub write is not required to validate the decision protocol; authentication and repository-write failures must themselves be reported as blocked rather than simulated as success.
