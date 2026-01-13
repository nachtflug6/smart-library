import re
import os
import uuid


def _slugify(text: str) -> str:
    text = text or ""
    text = os.path.splitext(text)[0]
    # replace non-alnum with hyphen
    text = re.sub(r"[^0-9a-zA-Z]+", "-", text)
    text = text.strip("-")
    return text.lower()


def _short_suffix() -> str:
    # short base36 suffix from uuid4
    v = uuid.uuid4().int & ((1 << 32) - 1)
    return base36(v)


def base36(num: int) -> str:
    if num < 0:
        raise ValueError("num must be non-negative")
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    if num == 0:
        return "0"
    s = []
    while num:
        num, rem = divmod(num, 36)
        s.append(alphabet[rem])
    return ''.join(reversed(s))


def generate_human_id(citation_key: str) -> str:
    """Generate a compact human-readable id from a citation_key (filename).

    Example: 'paper-title.pdf' -> 'paper-title-1a2b3'
    """
    base = _slugify(citation_key)
    if not base:
        base = "doc"
    # use a short suffix to avoid collisions
    suffix = base36(uuid.uuid4().int & 0xFFFFFF)[:6]
    return f"{base}-{suffix}"
