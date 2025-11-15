from __future__ import annotations

_PUNCT_STRIP = "()[]{}:,.;"

def _normalize_newlines(text: str) -> str:
    # Replace line breaks with spaces first
    return (text or "").replace("\r\n", "\n").replace("\r", "\n").replace("\n", " ")

def _collapse_whitespace(text: str) -> str:
    return " ".join((text or "").split())

def _normalize_hyphenation(text: str) -> str:
    # Remove artifacts like "- " or " -"
    return text.replace("- ", "-").replace(" -", "-")

def normalize_text(text: str) -> str:
    """
    General-purpose normalization:
    1. Newline flattening
    2. Lowercasing
    3. Hyphenation artifact cleanup
    4. Whitespace collapse
    5. Edge punctuation trim
    """
    s = _normalize_newlines(text)
    s = s.lower()
    s = _normalize_hyphenation(s)
    s = _collapse_whitespace(s)
    return s.strip(_PUNCT_STRIP)
