---
name: bootstrap-repo
description: Bootstrap or safely evolve a software repository from human-maintained PRD and EDD intent through implementation, validation, GitHub publication, and a PR-first cross-agent delivery policy. Use for repository birth or non-destructive re-bootstrap; not for ordinary feature execution.
---

# Bootstrap a Repository

Establish the smallest repository in which humans and coding agents can work autonomously through standard filesystem, Git, GitHub Issue, Pull Request, and CI artifacts.

## Preserve the intent model

Treat these as human-maintained canonical contracts:

- `docs/PRD.md`: Product Intent
- `docs/EDD.md`: Engineering Intent

Locate equivalent drafts when they are not yet normalized. Implementation, tests, Issues, PRs, README, and current code are evidence or derived state; none silently changes PRD/EDD semantics. If the requested bootstrap requires a product or engineering semantic decision, stop that portion and ask the user to resolve it.

GitHub Issues become the persistent Work Contract layer after bootstrap. Each Issue is one independently deliverable outcome, normally completed by one final delivery Pull Request rather than responsibility shared across multiple ordinary PRs. If one final PR cannot reasonably deliver the outcome, re-boundary the Issue before implementation. The default branch represents accepted implementation reality. Merge is not completion: only successful CI for the merged commit on the default branch completes the Work Contract.

## Resolve collaboration language

Before composing repository-facing Issue, PR, review summary, handoff, or status prose, resolve the language in this order: explicit repository or user instruction, scoped `AGENTS.md` policy, dominant language of human-maintained PRD/EDD, then the current settled human request. Explicit instruction wins over an old template, history, code comments, or technical source. Do not infer language from programming languages, dependency names, or identifiers. Write human prose in the resolved language while preserving technical terms, identifiers, commands, errors, paths, URLs, API names, and GitHub numbers verbatim. Never hardcode Chinese; English and other repository languages remain valid.

## Start with evidence

1. Read PRD, EDD, and applicable `AGENTS.md` files completely.
2. Inspect the target directory, Git state, manifests, CI, external integrations, and agent infrastructure. Prefer the bundled read-only probe:

   ```bash
   python <skill-dir>/scripts/inspect_repo.py --root <target-directory>
   ```

3. Classify the run as a new bootstrap or an existing re-bootstrap.
4. Read [the detailed workflow](references/workflow.md). Preserve unrelated or uncommitted work in an existing repository.
5. Research only stack, dependency, integration, and GitHub facts that affect the current result, using primary sources.

## Clarify only material decisions

Ask only when the answer cannot be inferred safely and changes product behavior, architecture, security/privacy, ownership, repository visibility, licensing, data handling, or destructive migration. Do not ask about routine conventions already determined by the EDD or ecosystem.

An explicit bootstrap request authorizes ordinary repository creation, validation, commit, and publication after required decisions are resolved. A dry run performs no mutation.

## Establish minimal agent infrastructure

Read [agent infrastructure](references/agent-infrastructure.md) when agents, MCP, plugins, permissions, or recurring automation are in scope. Prefer standard Git/GitHub/CI capabilities. Do not add orchestration, worktree, PR, CI, merge, or task-local-review skills merely to automate ordinary delivery.

Create or maintain a concise project `AGENTS.md` that establishes these invariants:

- Each Issue is one independently deliverable Work Contract and is normally completed by one final delivery PR; re-boundary work that cannot reasonably satisfy that ownership model.
- Issue-backed changes normally use an isolated branch or worktree and are delivered through a PR.
- PRs link Issues with exact `Refs #N` lines; agents do not use `Closes`, `Fixes`, or `Resolves` because merge must not auto-close the Work Contract.
- Another agent can reconstruct the handoff from PRD/EDD, linked Issue, commits, PR description/diff, tests, and CI—without private conversation state.
- Required verification must pass before merge.
- Merge only admits code to the default branch. Main CI success for the merged commit comments on and closes linked open Issues with the `completed` state reason; every non-success conclusion comments and leaves them open.
- PRD/EDD semantic changes require explicit human resolution.
- Repository-facing artifacts use the resolved collaboration language and preserve technical strings verbatim.

For every new GitHub repository bootstrap, add a lightweight PR template with non-closing Issue linkage, change summary, verification evidence, and PRD/EDD impact, plus the separate Main CI finalization workflow. Read [Main CI Issue finalization](references/issue-finalization.md) and adapt the bundled assets to the repository. An existing repository receives these files only through an explicit re-bootstrap migration. Do not turn the template into a bureaucratic checklist or couple Issue lifecycle code into the project's test jobs.

## Materialize conservatively

For a new repository, implement the smallest complete structure implied by PRD/EDD: typically README, AGENTS, license decision, ignore/config examples, source, tests, CI, and ecosystem configuration. Do not create speculative architecture, services, documentation trees, or agent infrastructure.

For an existing repository, perform delta analysis and make additive, minimal changes. Do not reinitialize, mass-format, replace a working toolchain, rewrite history, or create a duplicate remote.

## Validate, publish, and verify

Read [validation](references/validation.md) before declaring local completion and [GitHub publication](references/github.md) before creating or changing a remote.

Completion requires actual setup/build/test quality gates, CI parity, secret review, intended Git status, verified GitHub identity, a pushed default branch, and a checked first CI run. Configure CI on Pull Requests and default-branch pushes, then verify that the separate finalizer watches the exact CI workflow name and cannot act on PR CI. Never claim publication or CI success without evidence.

## Maintain the skill

When changing this protocol, use [the evaluation cases](references/evaluation.md). Preserve the two-contract intent model, PR-first cross-agent handoff, minimal infrastructure, non-destructive re-bootstrap, and honest publication claims.
