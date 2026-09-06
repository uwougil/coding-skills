# Bootstrap Workflow

Read this reference after inspecting the repository and classifying the run.

## Build a Project Model

Translate the three intent sources into a concise working model before editing:

- users and outcomes from the PRD;
- system boundaries, components, data, interfaces, constraints, and quality attributes from the EDD;
- the smallest currently due deliverable and acceptance criteria from milestones;
- selected stack and toolchain, with reasons grounded in the EDD and current research;
- unresolved decisions and risks;
- local validation commands;
- GitHub destination and CI expectations.

Do not create a new canonical project-model document by default. Keep the model in the task context and project it into the repository files. If a user decision changes intent, update the relevant PRD, EDD, or milestone rather than recording the decision only in generated files.

## Research Before Questions

Research only what can affect the current implementation. Prefer official documentation, specifications, primary repositories, and current package registries. Check version compatibility, supported runtimes, security implications, maintenance status, licensing, and integration constraints where relevant.

Separate findings into:

- facts resolved by sources;
- engineering defaults supported by strong conventions;
- genuine user decisions.

Ask only the last category. Batch related decisions, lead with the most blocking ones, and avoid an exhaustive questionnaire. If the user does not answer an optional preference, use the recommended default and state it. Do not infer repository visibility, destructive migration, ownership, secret handling, or a material product behavior.

## Mode A: New Repository Bootstrap

1. Normalize supplied drafts into `docs/PRD.md`, `docs/EDD.md`, and `docs/milestones/*.md` without silently changing their meaning.
2. Resolve material contradictions and update the intent sources with confirmed decisions.
3. Select the minimum viable architecture for the current milestone.
4. Create working source and at least one meaningful test or smoke test; avoid placeholder-only implementations.
5. Add repository documentation and automation that reflect actual commands.
6. Run the full local validation loop.
7. Initialize Git only if needed. Commit explicit paths so unrelated files are not swept in.
8. Create and push the GitHub repository, then verify the remote and CI.

The repository should normally include:

```text
README.md
AGENTS.md
LICENSE                 # after the license decision
.gitignore
.env.example            # when runtime configuration exists; never real values
docs/PRD.md
docs/EDD.md
docs/milestones/
src/                    # or the ecosystem's conventional equivalent
tests/                  # or conventional colocated tests
scripts/                # only scripts with current value
.github/workflows/ci.yml
<language-specific project configuration>
```

This is an outcome checklist, not a fixed tree. A VS Code extension, Rust workspace, web monorepo, desktop application, or service may need a different conventional structure.

## Mode B: Existing Repository Re-bootstrap

1. Capture `git status`, branch, remotes, current manifests, existing CI, tests, and relevant generated artifacts before editing.
2. Compare current PRD/EDD/milestones with implementation and identify deltas as missing, obsolete, conflicting, or already satisfied.
3. Research only new or changed requirements and their compatibility with the current stack.
4. Clarify architecture branches or migrations that cannot be made additive.
5. Add or modify only necessary infrastructure and implementation. Preserve unrelated changes and established conventions.
6. Run focused tests first, then the broader repository checks justified by the change.
7. Do not create a second GitHub repository when an appropriate remote already exists. Verify and use it. If the desired destination conflicts with the configured remote, ask before changing it.

Never use destructive cleanup, broad file replacement, repository reinitialization, or automatic history rewriting. If a migration truly requires removal or replacement, explain the exact scope and obtain the additional decision before proceeding.

## Progressive Disclosure of Engineering Intent

Do not split the EDD merely to make it look organized. Extract a section only when its details are substantial enough to maintain independently.

When extracting:

1. Move the detailed content to an appropriate file such as `docs/architecture/`, `docs/interfaces/`, or `docs/decisions/`.
2. Replace it in the EDD with a short summary and canonical relative link.
3. Do not duplicate the moved text.
4. Preserve engineering semantics. If a semantic change is needed, report it and treat it as an intent change, not document cleanup.
5. On the first extraction, create `docs/STRUCTURE_CHANGES.md`, label it as agent-maintained derived history rather than a source of truth, and record timestamp, old location, new location, reason, `semantic change: yes/no`, and affected links.

Do not create the structure-change log when no extraction occurs.
