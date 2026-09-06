import sluglib


def build_slug(title: str) -> str:
    return sluglib.slugify(title, allow_unicode=True)
