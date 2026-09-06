# Engineering Design

## Package layout

The repository is a static skill collection. Each skill is an independent package under `skills/<skill-name>/` with this conventional shape where applicable:

```text
SKILL.md
agents/openai.yaml
references/
scripts/
evals/
```

The five packages are intentionally independent: they may be installed separately and must not import one another at runtime. The root contains only collection documentation, validation, ignore rules, and CI.

`create-issue` may invoke an already authenticated `gh` CLI session through its stdlib-only wrapper. It must fail closed when repository identity or authentication is unavailable and must never store credentials.

## Source fidelity

Skill behavior is defined by each package's `SKILL.md`. Reorganization may change repository topology, but must preserve frontmatter, instructions, links, scripts, and authored evaluation semantics. Generated Python caches, temporary evaluation worktrees, and raw logs are excluded from version control.

## Validation

The root validator checks package presence, required frontmatter, UI metadata, UTF-8 readability, JSON evaluation assets, and the absence of machine-local paths. Focused standard-library tests exercise the bundled deterministic helpers. CI runs the same checks on Python 3.11.

## Distribution

The repository is pushed to a user-selected GitHub owner and visibility. No credentials are stored in the repository or passed through tracked files.
