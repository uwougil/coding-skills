# Project instructions

- `dependency-lock.json` is the declared dependency selection.
- `ci_config.json` controls the vendored module loaded by the CI-equivalent runner.
- Reproduce CI with `conda run -n base python run_ci.py`.
- Do not add compatibility fallbacks to business code unless the EDD requires them.
