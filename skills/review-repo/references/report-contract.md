# Report contract

## Findings

Order findings by severity: Critical, High, Medium, Low. Each finding must include title, category, direct evidence, expected behavior, actual behavior, consequence, bounded action, and confidence.

Copy repository-relative evidence paths exactly, including leading dots in hidden directories such as `.github/`.

Use these categories when possible: PRD Compliance, EDD Compliance, Work Contract Compliance, Delivery Provenance, Architecture Drift, Test Adequacy, Derived Documentation Drift, Agent Infrastructure, Accidental Complexity, Source-of-Truth Ambiguity.

Use `Work Contract Compliance` for a closed Issue whose acceptance criteria are missing from accepted code or tests. Use `Delivery Provenance` when a repository rule requires an Issue/PR chain for a material accepted change and that chain cannot be reconstructed. Record related PRD/EDD effects in status fields instead of duplicating one root cause across categories.

Severity reflects consequence, not volume:

- **Critical:** immediate severe security, privacy, irreversible-data, or broadly exploitable integrity failure.
- **High:** a core product promise, accepted Issue criterion, architecture boundary, or critical operational control is materially violated.
- **Medium:** a supported secondary path, verification guarantee, provenance chain, or maintainability boundary is materially weakened.
- **Low:** bounded real inconsistency with limited current impact.

## Status summaries

Use `compliant`, `partially compliant`, `non-compliant`, `ambiguous`, or `not assessable`, followed by concise evidence, for:

- PRD status;
- EDD status;
- Issue/PR provenance status.

Also state test confidence, architecture status, derived-document status, and agent-infrastructure assessment. Missing artifacts alone are not fabricated non-compliance.

## Issue candidates

For every finding considered for Issue creation, record its title, eligibility, and reason. Eligibility requires all six review-finding gates. Ambiguity, duplicates, low confidence, and semantic PRD/EDD changes must be ineligible.

## No-finding result

If no substantive finding passes the threshold, say so explicitly, summarize inspected evidence and verification limits, and do not manufacture low-value advice.
