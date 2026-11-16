import re
import unicodedata


def fold(value):
    """Accent-insensitive key for matching only; never use it in emitted answers."""
    value = unicodedata.normalize("NFD", str(value or "")).replace("đ", "d").replace("Đ", "D")
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def tokens(value):
    return set(fold(value).split())
