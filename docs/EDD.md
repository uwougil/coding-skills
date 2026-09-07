# Engineering Design

## Architecture

The repository is a static, independently installable skill collection under `skills/<skill-name>/`. Each package may contain `SKILL.md`, `agents/openai.yaml`, and only the references, scripts, or eval assets required by its protocol. The four packages do not import one another at runtime.

The shared engineering model is:

```text
PRD / EDD (human-owned intent)
  → GitHub Issue (Work Contract)
  → branch or worktree implementation
  → commits + Pull Request (Delivery / Handoff Contract)
  → CI and task-local review
  → default branch (accepted implementation reality)
  → independent review-repo audit
  → high-confidence finding through create-issue
```

Ordinary planning, branch/worktree handling, commits, pushes, PR creation, CI repair, review, merge, and Issue closure are host-agent and Git/GitHub capabilities. They are deliberately not modeled as skills or custom orchestration infrastructure.

## Authority and portability

PRD and EDD semantics change only through explicit human resolution. Issues scope individual work; PRs preserve delivery evidence. A handoff must be reconstructible from repository-visible artifacts and cannot depend on hidden reasoning, session state, or a particular Agent vendor.

`create-issue` uses an authenticated `gh` CLI session through a standard-library wrapper and fails closed on missing identity, authentication, duplicate checks, or review-finding eligibility. `.agents/skills/create-issue/` remains a byte-identical discovery mirror of the portable package.

## Validation and CI

The root validator checks the exact skill inventory, package structure, UTF-8/Python/JSON validity, mirror fidelity, retired-workflow absence, structured protocol manifests, and forbidden orchestration skills. Focused standard-library tests exercise bootstrap discovery, Issue backend guards, cross-skill protocol invariants, and review fixture generation. CI runs the same deterministic commands on pushes and Pull Requests.

Generated caches, temporary evaluation worktrees, raw model logs, local paths, and credentials are excluded from version control.
