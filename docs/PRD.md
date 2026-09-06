# Product Requirements

## Goal

Provide one portable GitHub repository containing four reusable Codex skills developed in the four conversations in this project:

- `bootstrap-repo`
- `implement-milestone`
- `fix-bug`
- `review-repo`

## Users and outcomes

Codex users should be able to browse the collection, copy one skill into their personal or project skill directory, invoke it by name, and find its supporting references, deterministic scripts, and evaluation assets in the same package.

## Scope

### In scope

- Preserve the four skill entrypoints and their behavior.
- Preserve directly used references, scripts, UI metadata, and authored evaluation definitions.
- Provide concise installation, validation, and repository-boundary documentation.
- Validate the package in local checks and GitHub Actions.

### Out of scope

- Creating a plugin or marketplace package.
- Installing the skills into another machine's Codex configuration.
- Rewriting the skill protocols or adding unrelated skills.
- Publishing local credentials, caches, generated fixture workspaces, or raw evaluation logs.
