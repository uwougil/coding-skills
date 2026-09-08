# Bootstrap Workflow

Read this reference after inspection and run classification.

## Build the project model

Translate the two intent sources into a concise working model:

- users and outcomes from PRD;
- architecture, boundaries, data, interfaces, constraints, and quality attributes from EDD;
- selected stack and toolchain;
- unresolved human decisions and risks;
- local validation commands;
- GitHub destination and CI expectations;
- Issue and Pull Request conventions for later work.

Resolve the collaboration language before drafting those conventions or any repository-facing artifact. Use the precedence and technical-string preservation rule in the skill entrypoint; propagate the resolved language into `AGENTS.md`, the PR template, Issue text, PR text, review summaries, handoffs, and status updates. Keep this policy portable: a repository may use English, Chinese, or another language.

Do not create another permanent planning document by default. Each GitHub Issue carries one independently deliverable Work Contract after bootstrap and is normally completed by one final delivery PR. If the outcome cannot reasonably be delivered that way, re-boundary the Issue before implementation instead of spreading completion responsibility across multiple ordinary PRs. Record a confirmed product or engineering decision in PRD/EDD only when the human has explicitly resolved it.

## Research before questions

Research only facts that affect the current repository. Separate primary-source facts, strong ecosystem defaults, and genuine user decisions. Ask only for the last category; never infer visibility, ownership, secret handling, destructive migration, or semantic product behavior.

## New bootstrap

1. Normalize supplied Product Intent and Engineering Intent into `docs/PRD.md` and `docs/EDD.md` without changing meaning.
2. Resolve material contradictions with the user.
3. Select the smallest viable architecture.
4. Create working source and meaningful tests.
5. For every new GitHub repository, add concise README/AGENTS, CI, a lightweight `Refs #N` PR template, and the separate Main CI Issue finalizer.
6. Run local validation and secret review.
7. Initialize Git, make a focused initial commit, publish the repository, and verify CI.

Typical structure, adapted to the ecosystem:

```text
README.md
AGENTS.md
LICENSE
.gitignore
.env.example
docs/PRD.md
docs/EDD.md
.github/PULL_REQUEST_TEMPLATE.md
.github/workflows/ci.yml
.github/workflows/issue-finalize.yml
.github/scripts/issue-finalize.js
src/
tests/
```

Do not create empty or future-facing trees just to match this example.

## Existing re-bootstrap

1. Capture branch, remotes, status, manifests, CI, tests, agent infrastructure, and recent history.
2. Compare PRD/EDD with accepted implementation reality and identify missing, obsolete, conflicting, or already-satisfied elements.
3. Research only changed requirements and compatibility.
4. Ask before semantic design changes or destructive migration.
5. Apply the smallest coherent delta and preserve unrelated work.
6. Run focused checks, then broader checks justified by the change.
7. Use the existing appropriate remote; deliver repository changes through a PR when Issue-backed or cross-agent handoff benefits.

## PR-first delivery policy

Keep the project `AGENTS.md` concise, but make repository-visible handoff reconstructible. A normal later lifecycle is:

```text
Issue → branch/worktree → implementation → commit → push → final delivery PR with Refs #N
      → PR CI + task-local review → repair → authorized merge → Main CI
      → success: comment + close Issue
      → non-success: comment + keep Issue open
```

One Issue normally has one final delivery PR; multiple ordinary PRs must not share responsibility for its completion. Merge is code admission, not Work Contract completion. Agents must not use GitHub auto-close keywords in PR bodies. The host coding agent and Git/GitHub own ordinary orchestration; the small post-Main-CI finalizer owns only status feedback and closure. Do not introduce a workflow engine or manager skill.

## Progressive disclosure of EDD

Extract substantial engineering detail only when it has independent lifecycle or multiple consumers. Move rather than duplicate it, retain an EDD summary and canonical link, preserve semantics, and record structural history. If extraction would change design, obtain human resolution first.
