def slugify(text: str) -> str:
    return text.lower().replace(" ", "-").encode("ascii", "ignore").decode("ascii")
