# Repository Validation

Read this reference before committing or publishing.

## Validate the Actual Stack

Derive commands from the chosen ecosystem and repository configuration. Do not invent generic commands or declare success because files exist.

Run, where applicable:

- dependency/configuration parsing and a clean setup using the declared lockfile strategy;
- a build or package step;
- meaningful basic tests, then the full justified test suite;
- formatter check, linter, type checker, and static analysis configured by the project;
- a smoke run of the primary CLI, service, extension build, application, or library import;
- CI workflow syntax and parity between CI and documented local commands.

Keep CI minimal: checkout, supported runtime setup, reproducible dependency installation, and the same core checks that pass locally. Pin versions at the granularity appropriate to the ecosystem and avoid unneeded matrices, services, caches, or release automation.

## Intent and Structure Review

Confirm that:

- the implementation satisfies the current milestone and does not contradict PRD or EDD;
- the structure follows the selected ecosystem rather than a hard-coded template;
- README setup and usage commands were actually exercised;
- `AGENTS.md` contains only repository-relevant guidance;
- no unnecessary project skill, MCP configuration, plugin, empty directory, or future-facing document was added;
- human and generated ownership is clear;
- any EDD extraction follows "extract, don't duplicate" and has a structure-change log.

## Git and Secret Review

Inspect `git status --short`, staged diff, ignored files, and tracked filenames. Ensure the commit contains only intended changes. Search tracked content for credible secret patterns using an available scanner when practical, and manually inspect configuration examples.

At minimum, reject tracked real `.env` files, private keys, credential files, access tokens, cookies, and machine-specific secrets. `.env.example` must contain placeholders only. Do not print discovered secret values; report only the file and remediation.

## Publication Evidence

Local success and remote success are separate. Record evidence for:

- local validation commands and exit status;
- commit identifier;
- remote URL and repository identity;
- pushed default branch;
- GitHub Actions run identifier, status, conclusion, and inspected failure logs when relevant.

If a required check cannot run because a tool, SDK, authentication, permission, or service is unavailable, state that limitation precisely. Do not relabel an unperformed check as passed.
