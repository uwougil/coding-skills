# coding-skills

一个可直接复用的 Codex skills 集合，收录五个围绕软件仓库工作的 skill：

| Skill | 用途 |
| --- | --- |
| [`bootstrap-repo`](skills/bootstrap-repo/) | 从 PRD、EDD 和 milestone 引导仓库，并完成验证与 GitHub 发布 |
| [`implement-milestone`](skills/implement-milestone/) | 在既定 PRD/EDD 约束下实现一个 milestone |
| [`fix-bug`](skills/fix-bug/) | 按“复现—证明—诊断—回归保护—最小修复—验证”修复缺陷 |
| [`review-repo`](skills/review-repo/) | 审计 Intent → Design → Execution → Implementation → Verification 的纵向一致性 |
| [`create-issue`](skills/create-issue/) | 将已确定的对话意图编译为 repository-aware GitHub Issue，并处理 duplicate 与 PRD/EDD 冲突 |

## 安装

将所需 skill 目录复制到 Codex 的个人 skill 目录即可：

```text
skills/<skill-name>/  ->  ~/.agents/skills/<skill-name>/
```

在 Codex 中可使用 `$skill-name` 调用，例如 `$review-repo`。每个 skill 的 `SKILL.md` 是入口；`references/`、`scripts/` 和 `evals/` 是按需使用的配套资源。

本仓库还为 `create-issue` 提供仓库级自动发现入口：`.agents/skills/create-issue/` 是 `skills/create-issue/` 的同步镜像。将 Codex 的工作目录设为本仓库根目录（或其子目录）后，重启 Codex 即可直接使用 `$create-issue`；也可以继续按上面的方式复制独立 skill 包。

## 本地验证

本仓库只依赖 Python 标准库：

```bash
python scripts/validate_skills.py
python skills/bootstrap-repo/scripts/test_inspect_repo.py
python skills/implement-milestone/scripts/tests/test_contract_snapshot.py
python skills/create-issue/scripts/gh_issue.py --help
python skills/create-issue/scripts/test_gh_issue.py
```

需要可用 Codex CLI 和对应服务时，可额外运行 `python skills/implement-milestone/scripts/run_behavior_evals.py` 做模型行为评测。该评测可能受服务配额和模型输出变化影响，因此不会在普通 CI 中自动启动。`review-repo` 的评测定义与已保存的结构化结果位于 `skills/review-repo/evals/`。

## 仓库边界

这里只发布五个 skill 包，不包含本机 Codex 配置、凭据、缓存、Python 字节码、临时评测工作目录或原始评测日志。
