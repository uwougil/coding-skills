# Agent Infrastructure Assessment

Read this reference only when agent workflows, external systems, Codex configuration, MCP, plugins, permissions, or repository automation are in scope.

Recheck current official Codex documentation before relying on a path or feature that may have changed. As of 2026-09-06, the supported project locations include repository skills under `.agents/skills/<skill-name>/SKILL.md`, project-scoped MCP configuration under `.codex/config.toml` for trusted projects, and hierarchical repository guidance in `AGENTS.md`.

## Decision Matrix

| Mechanism | Add it when | Do not add it when |
| --- | --- | --- |
| `AGENTS.md` | Codex needs repository-specific setup, commands, constraints, generated-file ownership, or safety rules | The content merely repeats README usage or global policy |
| Project skill | A repository-specific workflow will recur, has several non-obvious steps, and benefits from a stable protocol or reusable resources | It is a one-off task, a short command, or generic knowledge |
| Project MCP | Codex needs durable access to an external tool/context source and existing CLI, API, or plugin support is inadequate | A normal CLI or authenticated API is sufficient, or the integration is only speculative |
| Plugin | A stable installable capability, existing mature integration, or bundled skill-plus-connector materially lowers maintenance cost | The need is personal, experimental, repository-only, or already covered by local tools |
| Permissions/rules | A narrow repository workflow needs durable least-privilege execution boundaries | Broad permissions are requested only for convenience |

Default to no new skill, MCP server, or plugin. A positive decision must name the recurring workflow or external capability, why current tools are insufficient, ownership/maintenance cost, credentials and data exposed, and how the integration will be tested.

Ordinary planning, branch/worktree creation, commits, pushes, Pull Requests, CI execution, task-local review, and authorized merge belong to the host coding agent plus Git/GitHub. A small repository workflow may finalize linked Issues after Main CI; this is standard GitHub automation, not a reason to add orchestrator, manager, CI, merge, or task-review skills.

## Project Skills

Place a repository-wide skill at `.agents/skills/<name>/SKILL.md`; use a deeper `.agents/skills` directory only when the workflow belongs to that subtree. Keep one focused job per skill. Use scripts only for repeated deterministic work and references only for conditional detail.

Do not copy this personal bootstrap skill into every target repository. Create a project skill only when the target itself has a recurring specialized workflow, such as release packaging, dataset normalization, or a fragile domain-specific validation sequence.

## MCP

Prefer an existing authenticated CLI or maintained plugin before authoring an MCP server. If MCP is justified, use project-scoped `.codex/config.toml` only in a trusted repository, keep secrets outside the file, document authentication without exposing credentials, and verify the server and required tools from the actual Codex host.

Official reference: https://learn.chatgpt.com/docs/extend/mcp

## Plugins

Inspect currently available plugins before proposing a new one. Installing or creating a plugin is a separate environment change; do it only when explicitly required by the intent sources or confirmed in clarification. Do not install a plugin merely because it is available.

Use a local skill while a workflow is still personal or evolving. Use a plugin when distributing stable skills, packaging a connector, or sharing a capability with a team. Keep repository code independent of a personal plugin unless that dependency is documented and reproducible for collaborators.

Official references:

- https://learn.chatgpt.com/docs/build-plugins
- https://developers.openai.com/plugins/

## AGENTS.md and Permissions

Keep root `AGENTS.md` concise and operational:

- authoritative intent files and generated-file ownership;
- setup, test, lint, format, build, and type-check commands that actually work;
- architecture boundaries that agents could otherwise violate;
- one independently deliverable Work Contract per Issue, normally one final delivery PR per Issue, Issue-backed branch/worktree isolation, `Refs #N` linkage, reconstructible handoff evidence, required-verification merge gates, and the invariant that only Main CI success completes and closes a Work Contract;
- secret-handling and external-mutation constraints;
- any repository-specific completion checks.

Use nested `AGENTS.override.md` only for a subtree with genuinely different commands or constraints. Do not encode broad machine policy or credentials in the repository.

Official reference: https://learn.chatgpt.com/docs/agent-configuration/agents-md
