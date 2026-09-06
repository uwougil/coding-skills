def normalize_title(text: str) -> str:
    return text.strip().replace("  ", " ")


def title_length(text: str) -> int:
    return len(normalize_title(text))


def has_title(text: str) -> bool:
    return bool(normalize_title(text))
