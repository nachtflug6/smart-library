from __future__ import annotations

try:
    from thefuzz import fuzz
except Exception:
    fuzz = None  # optional

def verify_string_in_string(term: str, text: str, *, fuzzy: bool = True, tolerance: int = 80) -> bool:
    """
    Return True if 'term' appears in 'text' (case-insensitive).
    If fuzzy=True and 'thefuzz' is available, use partial_ratio with tolerance (0..100).
    """
    t = (term or "").lower().strip()
    if not t:
        return False
    s = (text or "").lower()
    if not fuzzy or fuzz is None:
        return t in s
    return fuzz.partial_ratio(t, s) >= int(tolerance)