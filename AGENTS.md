# Repository Instructions

## Source and ownership

- Each `skills/<name>/SKILL.md` is the authoritative entrypoint for that skill.
- Supporting references, scripts, and eval definitions belong to their owning skill and should remain linked from its entrypoint or evaluation workflow.
- Root `README.md`, `scripts/validate_skills.py`, and CI are derived packaging and verification files; keep them synchronized with the five skill directories.

## Verification

Run the commands documented in `README.md` before committing. Do not add third-party runtime dependencies for repository validation.

## Scope and safety

- Keep the repository limited to `bootstrap-repo`, `implement-milestone`, `fix-bug`, `review-repo`, and `create-issue` plus the minimal packaging files.
- Preserve each skill's behavioral contract and evaluation assets; do not silently weaken instructions or assertions while reorganizing files.
- Never commit credentials, tokens, private keys, local Codex configuration, generated caches, or raw evaluation logs.
- Changes that alter a skill's behavior require updating its relevant evaluation or documentation and rerunning the focused checks.
