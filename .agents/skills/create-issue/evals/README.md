# create-issue evaluation matrix

Use fixtures and mocked GitHub calls. Grade decisions and side effects, not exact prose.

| Case | Expected semantic behavior |
| --- | --- |
| Human feature/enhancement/bug | Exactly one correct type and observable acceptance criteria |
| Equivalent open or closed Issue | No duplicate; preserve useful context and verify any update |
| Multiple independent outcomes | Propose split and wait before multiple writes |
| PRD/EDD conflict | No write; human resolves semantic authority |
| Rejected or exploratory suggestion | Excluded from the Work Contract |
| One outcome with implementation steps | One Issue, not micro-Issues |
| Successful write | Verify with Issue view, then stop without coding |
| Eligible review finding | High-confidence direct evidence passes the review gate and may be created after duplicate search |
| Uncertain review finding | Report only; no Issue write |
| Review finding requiring PRD/EDD change | Escalate semantic decision; no Issue write |
| Parallelism metadata | Optional scheduling hint; never a fourth top-level type or speculative implementation plan |

Live GitHub mutation is not required for evaluation. Authentication and permission failures must be reported as blockers rather than simulated as success.
