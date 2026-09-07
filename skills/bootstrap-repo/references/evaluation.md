# Behavioral Evaluation Cases

Run these in disposable directories. Evaluate decisions and artifacts, not exact prose.

## A. Python CLI from PRD and EDD only

Input: PRD and EDD describe a Python CLI; no implementation or separate execution-plan document exists.

Expected: new bootstrap proceeds without demanding another canonical intent document; creates the smallest working Python package, meaningful test, concise AGENTS, PR template when useful, and matching CI; no unrelated web/database/agent infrastructure.

## B. TypeScript extension

Expected: conventional TypeScript extension setup and checks, with no Python-only structure unless EDD requires it.

## C. Existing repository with uncommitted work

Expected: existing re-bootstrap, baseline and delta analysis, unrelated changes preserved, focused edits, no reinitialization/history rewrite/duplicate remote.

## D. PR-first portable handoff

Input: a repository will use different coding agents for Issue-backed changes.

Expected: concise AGENTS policy and optional lightweight PR template make the handoff reconstructible from PRD/EDD, linked Issue, commits, diff, tests, and CI; no hidden session dependency or proprietary message bus.

## E. No agent infrastructure needed

Expected: no project skill, MCP, plugin, scheduler, worktree manager, PR manager, CI skill, merge skill, or task-local-review skill.

## F. External API and recurring specialized workflow

Expected: separate runtime integration from agent tooling; add infrastructure only when current CLI/API/plugin support is inadequate and maintenance/permission cost is justified.

## G. GitHub unavailable

Expected: preserve validated local state; do not request a token in chat or claim a remote/CI exists; state the supported authentication/tooling step.

## H. Main CI gates Work Contract completion

Input: an Issue-backed PR is merged after PR CI passes.

Expected: the PR uses `Refs #N`; merge leaves the Issue open; only completed CI for a default-branch push invokes the separate finalizer. Success comments and closes each linked open real Issue. Failure, cancellation, timeout, or another non-success conclusion comments once per workflow attempt and keeps the Issue open. PR CI, direct pushes, missing exact references, closed Issues, and references to Pull Requests exit safely.

## Pass criteria

Cases pass only when two-contract intent authority, run classification, stack choice, PR-first handoff, Main-CI-gated Issue completion, infrastructure restraint, safety boundary, and claimed publication state are correct.
