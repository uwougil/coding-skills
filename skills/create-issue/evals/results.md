# `create-issue` evaluation status

The deterministic wrapper tests cover GitHub remote parsing, exact type labels, optional scheduling labels, body-file guards, JSON list decoding, and fail-closed review-finding eligibility. The repository protocol tests validate both source modes, the three-type taxonomy, PRD/EDD semantic guards, and mirror fidelity.

Behavior cases are defined in [manifest.json](manifest.json) and [README.md](README.md). Live Issue creation is intentionally excluded from dry-run evaluation; every real invocation must still verify remote identity, authentication, open-and-closed duplicate results, and the final Issue view.
