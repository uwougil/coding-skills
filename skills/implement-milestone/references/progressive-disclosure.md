# Content-preserving EDD extraction

Read this reference only when an EDD section relevant to the current Milestone is a credible extraction candidate.

## Qualification

Extraction is optional, not a documentation quota. It is warranted when the relevant section has become clearly complex, is referenced by multiple modules, or has an independent change lifecycle, and moving it will make ownership and navigation clearer.

Do not reorganize unrelated EDD sections. Do not extract merely because a section is long. Do not use extraction to broaden the Milestone or conceal a design revision.

If the move requires changing module boundaries, dependency direction, runtime behavior, data semantics, interface/error semantics, or security/privacy policy, it is not content-preserving. Classify it as a genuine EDD design issue and stop for a user decision.

## Choose one canonical destination

Follow an existing repository convention. Otherwise choose the narrowest appropriate location:

- `docs/architecture/` for component structure, dependency, runtime, or data design;
- `docs/interfaces/` for API, protocol, event, schema, or compatibility contracts;
- `docs/decisions/` for an already-made engineering decision whose rationale and consequences have an independent lifecycle.

Do not create parallel canonical descriptions. The derived document becomes canonical for the moved detail; EDD keeps only a stable summary and link.

## Move-not-copy procedure

1. Record the exact source section boundaries and all inbound links or anchors.
2. Create one destination document with a clear title, ownership/context statement, and the moved content.
3. Move the detailed assertions, tables, diagrams, examples, and constraints. Preserve their meaning; make only mechanical heading, anchor, and relative-link adjustments.
4. Replace the source detail in EDD with a concise summary of its role and a relative link to the canonical destination.
5. Search the repository for references to the old heading, anchor, or path and update every necessary link.
6. Compare the diff against the pre-move content. Confirm that no normative statement was lost, duplicated, weakened, or strengthened.
7. Run available documentation/link checks.
8. Write the structural change log and include the move in the final report.

If exact textual preservation is impractical because headings or relative links must change, preserve semantic assertions one-for-one and record the mechanical edits.

## Structural change log

Use the repository's existing architecture/documentation change log when present. Otherwise create or append to `docs/architecture/STRUCTURAL_CHANGES.md` with:

- date and current Milestone;
- original EDD heading/path;
- canonical destination;
- reason the section qualified for extraction;
- links/anchors updated;
- statement that the operation was content-preserving;
- any mechanical formatting or link changes.

The log records document topology, not a new design decision. If the statement that semantics were preserved is not true, revert the extraction and report the design conflict.
