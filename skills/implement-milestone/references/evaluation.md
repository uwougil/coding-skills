# Behavioral evaluation

This reference is for maintaining or evaluating the Skill itself. It is not part of ordinary Milestone execution.

Run `python scripts/run_behavior_evals.py` from the Skill directory. The runner creates disposable repositories, invokes `$implement-milestone` in non-mutating/read-only mode, requires structured JSON decisions, and checks semantic invariants. It needs an authenticated `codex` CLI and can take several minutes.

Use repeatable `--case <id>` arguments to run selected cases, `--timeout <seconds>` to change the per-case limit, and `--json` for machine-readable results. The temporary repositories are removed automatically.

The baseline suite covers:

1. `ordinary_feature` — proceeds with a normal feature and proportional unit tests.
2. `explicit_non_goal` — keeps avatar upload outside a profile-display Milestone.
3. `edd_conflict` — blocks an external network service forbidden by EDD.
4. `integration_boundary` — selects integration testing for service-to-database behavior.
5. `progressive_disclosure` — recognizes a complex, shared, independently versioned protocol section as a content-preserving extraction candidate.
6. `future_milestone_guard` — excludes CSV export assigned to the next Milestone even when nearby code makes it convenient.

These evals test decision behavior rather than exact prose. They do not prove arbitrary implementations correct; keep the completion gate, repository-native tests, and diff review in every real run.
