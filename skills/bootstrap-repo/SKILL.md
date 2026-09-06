---
name: bootstrap-repo
description: Bootstrap or safely evolve a software repository from PRD, EDD, and milestone intent through research, clarification, implementation, validation, GitHub publication, and CI verification. Use for new-repository materialization or non-destructive re-bootstrap; not for generic scaffolding without these intent sources.
---

# Bootstrap a Repository

Compile product intent into a minimum viable architecture that runs, tests, and can be maintained by agents and humans. Finish a new-repository run only after publishing the repository to the user's GitHub account and checking the first CI run, unless authentication, permissions, or an explicitly requested dry run prevents publication.

## Preserve the Intent Model

Treat these human-maintained documents as the canonical intent sources:

- `docs/PRD.md`: product intent
- `docs/EDD.md`: engineering intent
- `docs/milestones/*.md`: execution intent

Locate and use equivalent user-supplied drafts when they have not yet been placed at those paths. Do not elevate README files, existing code, generated documentation, or stale project notes above these sources. Existing code is implementation evidence, not a higher-priority requirement.

When the sources conflict, identify the conflict and its impact. Resolve factual questions through research; ask the user only when the resolution changes product behavior, architecture, security, privacy, ownership, repository visibility, or another material preference. Record confirmed decisions in the appropriate intent source so the three-source model remains coherent.

## Start With Evidence

1. Read the three intent sources and applicable `AGENTS.md` instructions completely.
2. Inspect the target directory, Git state, manifests, CI, external integrations, and existing agent infrastructure. Prefer the bundled read-only probe:

   ```bash
   python <skill-dir>/scripts/inspect_repo.py --root <target-directory>
   ```

3. Classify the run:
   - **New bootstrap:** there is no meaningful implementation or repository history, or the user explicitly chose a new repository.
   - **Existing re-bootstrap:** meaningful code, project configuration, history, or infrastructure already exists.
4. Read [the detailed workflow](references/workflow.md). For an existing repository, take a baseline before editing and preserve unrelated or uncommitted work.
5. Research the selected stack, current framework and dependency behavior, third-party integrations, and relevant agent capabilities using authoritative primary sources. Resolve discoverable facts before asking questions.

## Clarify Only Decisions

After research, ask a small, prioritized set of questions only when the answer materially changes the result and cannot be inferred safely. Each question must include the discovered context, viable options, tradeoffs, a recommended default, and why the user must decide.

Typical required decisions include unresolved product behavior, incompatible architecture branches, GitHub owner/name/visibility, licensing, data handling, authentication, and security boundaries. Do not ask about routine folder names, formatter defaults, test placement, or other decisions covered by the EDD or strong stack conventions.

Explicit invocation authorizes the ordinary repository-creation sequence for a new bootstrap once required parameters are resolved. Do not ask a second generic confirmation to create, commit, or push the repository. A request for a dry run is different: perform research, assessment, and a proposed project model, but make no local or remote mutations.

## Assess Agent Infrastructure

Read [agent infrastructure](references/agent-infrastructure.md) when the project mentions agents, external systems, MCP, plugins, skills, permissions, or recurring automated workflows.

Apply the minimal-infrastructure policy:

- Add a project skill only for a repository-specific workflow that is recurring, multi-step, and benefits from a stable protocol.
- Add project-scoped MCP only when Codex needs durable external tools or context that existing CLI, API, or plugin support cannot reasonably provide.
- Install or create a plugin only when a mature plugin or distributable bundle clearly reduces ownership cost and the requirement is explicit or confirmed.
- Add `AGENTS.md` with concise repository-specific setup, verification, and safety guidance. Add nested overrides only for genuinely different subtrees.

Do not create agent infrastructure merely because the software uses agents.

## Materialize Conservatively

For a new repository, implement the smallest complete structure implied by the EDD. The usual baseline is README, `AGENTS.md`, license decision, `.gitignore`, `.env.example` when configuration exists, canonical intent documents, source, tests, narrowly useful scripts, CI, and language-specific project configuration. Adapt names and layout to the ecosystem; never force Python conventions onto another stack.

Do not pre-create empty architecture, decision, interface, schema, benchmark, example, Docker, or packaging trees. Create components such as API, database, frontend, extension, or desktop runtime only when current intent requires them.

For an existing repository, perform delta analysis and make additive, minimal patches. Never empty, reinitialize, mass-reformat, or overwrite the project. Do not replace a working toolchain simply to match a preferred template. Stage and commit only the intended bootstrap changes.

Maintain README, `AGENTS.md`, ignore/config examples, source, tests, scripts, CI, derived docs, schemas, and release metadata as agent/tooling-owned projections of intent. Do not introduce another human source of truth such as `ROADMAP.md`, `PROJECT_STATE.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, or `glossary.md` unless the project explicitly needs it.

## Validate, Publish, Verify

Read [validation](references/validation.md) before declaring the local repository complete. Fix failures and rerun relevant checks. Then read [GitHub publication](references/github.md) for new repositories or repositories that need a remote.

For a new bootstrap, complete this end state:

1. The selected build/package configuration parses and setup succeeds.
2. Basic tests and configured lint/format checks pass.
3. CI is syntactically valid and mirrors the local checks.
4. No secret or private credential is tracked.
5. The Git working tree contains only expected changes.
6. GitHub authentication and destination ownership are verified.
7. The real GitHub repository exists, the remote is correct, and the default branch is pushed.
8. The first GitHub Actions run is found and checked; wait for it when practical and bounded.

Never claim publication or CI success from intended commands alone. If authentication or permission is missing, stop before the remote mutation, preserve the validated local repository, and state the exact authentication step needed. Never request a PAT, token, or secret in chat or in a tracked file.

## Maintain the Skill

When changing this skill, use [the evaluation cases](references/evaluation.md) to guard its cross-stack, non-destructive, minimal-infrastructure, and honest-publication behavior.
