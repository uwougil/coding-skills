# Slug integration design

Business code must call `sluglib.slugify(text, allow_unicode=True)`. CI loads the dependency selected by `dependency-lock.json`; `ci_config.json` must point to that same vendored version.
