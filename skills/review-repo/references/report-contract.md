# Report Contract

Use this contract to keep reports prioritized, reproducible, and resistant to finding inflation.

## Severity

- **Critical:** A broadly reachable defect can cause catastrophic security/privacy loss, irreversible data loss, or complete failure of a defining product guarantee. Use sparingly.
- **High:** A core PRD promise, milestone acceptance criterion, architecture boundary, or security/privacy control is materially violated in supported use.
- **Medium:** A real gap creates bounded incorrect behavior, meaningful maintenance/operational risk, or inadequate verification, but does not defeat the product's defining path.
- **Low:** A confirmed, limited issue worth addressing that has small impact. Omit low-value style and preference comments.

Severity describes impact and reach, not review confidence.

## Categories

Use one primary category per finding:

- `PRD Compliance`
- `EDD Compliance`
- `Milestone Compliance`
- `Architecture Drift`
- `Test Adequacy`
- `Derived Documentation Drift`
- `Agent Infrastructure`
- `Accidental Complexity`
- `Source-of-Truth Ambiguity`

Mention secondary dimensions in the explanation instead of duplicating the finding.

## Finding shape

```markdown
### [High] Short consequence-oriented title

- Severity: High
- Category: PRD Compliance
- Evidence: `docs/PRD.md:18-24`; `src/store.py:41-58` (`save_note`); `tests/test_store.py:73`
- Expected behavior: The PRD requires all note creation to work offline and forbids a mandatory remote dependency.
- Actual behavior: `save_note` always posts to the configured API before returning; the test replaces the network call with a mock.
- Why it matters: A supported offline user cannot create a note, and content crosses a boundary the product promise excludes.
- Recommended action: Make the local store authoritative and move synchronization behind an explicit optional adapter, or obtain and record an approved PRD/EDD change.
- Confidence: High
```

Evidence may span multiple paths, but keep the range tight. Use `Confidence: High | Medium | Low`. Lower confidence when behavior depends on an unobserved runtime, missing generated artifact, or an inference that could not be executed.

## Status vocabulary

For PRD, EDD, and milestone status, use:

- `Compliant in reviewed scope`
- `Partially compliant`
- `Non-compliant`
- `Unable to assess`
- `Not applicable to reviewed scope`

State the reviewed scope and the strongest evidence or gap in one or two sentences. Do not convert missing PRD/EDD/milestone files into fabricated compliance findings.

For tests, architecture, documentation, and agent infrastructure, give calibrated prose and explicitly distinguish inspected evidence from executed checks.

## Required report order

1. **Executive Summary** — scope, overall conclusion, top risks, and important limits.
2. **Critical/High findings** — say `None` when there are none.
3. **Medium findings** — say `None` when there are none.
4. **Low findings** — include only useful items; otherwise say `None reported`.
5. **PRD compliance status**
6. **EDD compliance status**
7. **Milestone compliance status**
8. **Test confidence**
9. **Architecture drift status**
10. **Derived-doc drift status**
11. **Agent infrastructure assessment**
12. **Recommended next actions** — ordered by risk reduction and decision dependency.

Do not hide a High finding in a summary table only. Do not repeat one root cause under several dimensions. When there are no substantive findings, state that clearly and explain the evidence and review limits that support the conclusion.
