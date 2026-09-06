def slugify(text: str, *, allow_unicode: bool = False) -> str:
    value = text.lower().replace(" ", "-")
    if allow_unicode:
        return value
    return value.encode("ascii", "ignore").decode("ascii")
