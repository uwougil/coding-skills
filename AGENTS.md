# Repository Instructions

## Contracts

- `docs/PRD.md` and `docs/EDD.md` are human-maintained Product Intent and Engineering Intent. Never change their semantics without explicit human resolution.
- GitHub Issues are Work Contracts. Issue-backed changes should normally use an isolated branch or worktree and be delivered through a Pull Request.
- A Pull Request is the repository-visible Delivery / Handoff Contract. Another agent must be able to reconstruct the work from PRD/EDD, the linked Issue when present, commits, PR description and diff, tests, and CI without private conversation state.
- Do not merge Issue-backed work while required verification is failing. The default branch is accepted implementation reality, not authority to silently override PRD/EDD.

## 协作语言

- Issue、PR、review summary、handoff 和 repository-facing status 中的人类说明，使用按以下顺序解析出的协作语言：显式仓库或用户指令 > 当前作用域的 `AGENTS.md` 政策 > 人维护的 PRD/EDD 的主要语言 > 当前已确定的人类请求。
- 显式指令优先于旧 PR 模板、历史对话、代码注释和技术资料；不要根据编程语言、依赖名称或标识符推断协作语言。
- 人类说明使用解析出的语言，但保留技术术语、标识符、命令、错误信息、文件路径、URL、API 名称和 GitHub 编号的原文。
- 该规则必须可迁移，不得把中文硬编码为唯一语言；English 和其他仓库语言同样有效。

## Repository maintenance

- Keep exactly `bootstrap-repo`, `create-issue`, `fix-bug`, and `review-repo` under `skills/`; do not add orchestration, merge, CI, or task-local-review skills.
- `.agents/skills/create-issue/` is a discovery mirror of `skills/create-issue/`; keep tracked files byte-for-byte synchronized.
- Keep skill entrypoints, references, scripts, eval manifests, root docs, validator, and CI consistent.
- Run every deterministic command in `README.md` before delivery. Preserve unrelated work and never commit credentials, caches, generated workspaces, or raw model logs.
