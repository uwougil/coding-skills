# Official capability notes used by `review-repo`

Research date: 2026-09-06. These notes capture the official Codex guidance that shaped this skill; they are not a substitute for checking the current product documentation when the host changes.

## Skills

Official guide: <https://developers.openai.com/codex/skills> (currently served from ChatGPT Learn as “Build skills”).

- A skill is a directory with required `SKILL.md` metadata and optional `scripts/`, `references/`, `assets/`, and `agents/openai.yaml`.
- Skill selection starts from name and description, then loads `SKILL.md`; this is progressive disclosure. Descriptions should be concise, discriminating, and front-load trigger words.
- Prefer focused instructions over scripts. Add scripts only for deterministic, repeatable work. Test prompts and validate the skill structure.
- Standalone local skills are suitable for authoring and repo/user scope; plugins are the distribution mechanism when connectors or multiple skills are needed.

Applied here: the entrypoint is focused and explicit about the review boundary; detailed method and report contract are references; the inventory helper is read-only and deterministic; no MCP or plugin dependency is declared.

## Multi-agent workflows

Official guide: <https://developers.openai.com/codex/multi-agent> (currently served from ChatGPT Learn as “Subagents”).

- Parallel agents are most useful for independent, read-heavy exploration, tests, triage, and summarization; overlapping write work increases conflicts and coordination cost.
- A good delegation prompt states the division of work, whether to wait for all agents, and the summary format to return. Subagents inherit the parent permission mode.

Applied here: subagents are optional, bounded to independent dimensions, forbidden to edit, and required to return concise evidence/counter-evidence to the lead reviewer for source-of-truth interpretation and deduplication.

## Repository code review

Official guide: <https://developers.openai.com/codex/code-review> (currently served from ChatGPT Learn as “Code review”).

- Codex review is intended to inspect changes and report prioritized, actionable findings without changing the working tree.
- Review scope can be a base branch, uncommitted changes, a commit, or custom criteria. Findings should be evidence-linked and can be followed up for narrower review.

Applied here: the default mode is read-only, prioritizes material findings, preserves worktree changes, and requires exact paths, symbols, tests, or command results for evidence.

## Project instructions

Official guide: <https://developers.openai.com/codex/guides/agents-md> (currently served from ChatGPT Learn as “Custom instructions with AGENTS.md”).

- Codex loads one applicable global instruction file, then one file per directory from project root to the current directory; nearer files appear later and override earlier guidance.
- The combined instruction size is bounded, so large guidance should be split deliberately.

Applied here: the reviewer resolves the applicable `AGENTS.md` / override chain and accounts for directory scope before assessing commands, boundaries, or evidence.

## Scope note

These pages describe host capabilities and conventions, not a semantic repository-review oracle. The review method therefore treats PRD/EDD as human-owned semantic authority, Issues as Work Contracts, PRs as Delivery/Handoff evidence, and unresolved semantic disagreement as a human decision rather than an invented design.
