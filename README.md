# coding-skills

一个面向 Agent 工程协作的四 skill 协议库：长期意图由人维护，GitHub Issue 承载工作契约，Pull Request 承载交付与跨 Agent 移交，Git 默认分支表示已接受的实现现实，Main CI 是 Issue 完成的最终自动验收门槛。

```text
PRD / EDD → create-issue → Issue → builder / fix-bug → PR (`Refs #N`) → PR CI → merge → main CI
                                                                                                ├─ success → comment + close Issue
                                                                                                └─ non-success → comment + keep Issue open

                         create-issue ← material finding ← review-repo automation
```

| Skill | 稳定职责 |
| --- | --- |
| [`bootstrap-repo`](skills/bootstrap-repo/) | 建立或安全演进仓库：PRD/EDD、源码、测试、CI、GitHub 和 PR-first 协作约定 |
| [`create-issue`](skills/create-issue/) | 将已确定的人类意图或高置信度仓库审查 finding 编译为 GitHub Issue |
| [`fix-bug`](skills/fix-bug/) | 为 bug 工作提供 evidence-first 调试与 PR-ready 验证协议 |
| [`review-repo`](skills/review-repo/) | 作为独立自动化审查协议，检查多次变更后仓库的语义健康度 |

`docs/PRD.md` 和 `docs/EDD.md` 是人维护的长期产品与工程意图。Issue 是可独立理解的 Work Contract；PR 是标准 Delivery / Handoff Contract。PR 使用 `Refs #N` 关联 Issue，merge 本身不会关闭 Issue；默认分支 Main CI 成功后，独立的 `issue-finalize.yml` 才会自动评论并关闭 Issue，非成功结果则评论并保持 Issue Open。分支、worktree、提交、推送、PR、CI 修复与普通合并仍由具备能力的宿主 Agent 和 Git/GitHub 完成，不需要额外的编排 skill。

`bootstrap-repo` 的新默认生命周期只自动应用于未来 bootstrap 或显式 re-bootstrap 的仓库。已有仓库需重新运行 bootstrap 的 GitHub 模板迁移，提供主 CI workflow 的准确 `name:`，审阅冲突后再使用 `--overwrite`；不会被本仓库更新自动改写。

Issue、PR、review summary、handoff 和状态说明遵循根目录 `AGENTS.md` 的协作语言优先级；技术术语、标识符、命令、错误信息、路径、URL、API 名称和 GitHub 编号保持原文。

## 安装与发现

将需要的目录复制到个人或项目 skill 目录：

```text
skills/<skill-name>/  ->  ~/.agents/skills/<skill-name>/
```

每个 `SKILL.md` 是入口，`references/`、`scripts/` 和 `evals/` 是按需资源。`.agents/skills/create-issue/` 是 `skills/create-issue/` 的字节级同步镜像，使本仓库内的 `$create-issue` 可被自动发现。

## 验证

CI 与本地运行相同的确定性检查：

```bash
python scripts/validate_skills.py
python scripts/test_protocol_contracts.py
python skills/bootstrap-repo/scripts/test_inspect_repo.py
python skills/bootstrap-repo/scripts/test_github_templates.py
node skills/bootstrap-repo/scripts/test_issue_finalize.js
python skills/create-issue/scripts/test_gh_issue.py
python skills/fix-bug/scripts/capture_repro.py --help
python skills/review-repo/scripts/repo_inventory.py --help
python skills/review-repo/evals/build_fixtures.py
```

需要可用 Codex CLI 和服务时，可额外运行 `python skills/review-repo/evals/run_evals.py --rebuild`。模型行为评测会受配额与模型变化影响，因此不作为普通 CI 的确定性门禁。

本仓库不包含凭据、缓存、临时评测工作区、原始模型日志，也不引入 workflow engine、任务调度器、PR/CI/merge manager 或 Agent 专用消息总线。
