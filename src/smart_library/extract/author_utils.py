"""Author name cleaning and formatting utilities."""
import re
from typing import List

_PARTICLES = {"de", "van", "der", "den", "von", "da", "dos", "del", "di", "la", "le", "du", "das"}


def _title_token(tok: str) -> str:
    """Convert a token to title case, handling particles and special cases."""
    if not tok:
        return tok
    # Keep initials (A., B.-C.) as-is
    if re.match(r'^[A-Z]\.$', tok):
        return tok
    # Handle hyphenated parts: Smith-Jones -> Smith-Jones
    parts = tok.split("-")
    titled = []
    for p in parts:
        if not p:
            continue
        low = p.lower()
        if low in _PARTICLES:
            titled.append(p[0].upper() + p[1:].lower())
        else:
            titled.append(p[0].upper() + p[1:].lower() if len(p) > 1 else p.upper())
    return "-".join(titled)


def _split_first_last(tokens: List[str]) -> tuple[List[str], List[str]]:
    """Split tokens into first/middle names and last name(s).
    
    Heuristic: Last name is the final token plus any preceding particles.
    """
    if not tokens:
        return [], []
    
    # Start from the end
    i = len(tokens) - 1
    last_tokens = [tokens[i]]
    i -= 1
    
    # Include preceding particles in last name
    while i >= 0 and tokens[i].lower() in _PARTICLES:
        last_tokens.insert(0, tokens[i])
        i -= 1
    
    first_middle = tokens[: i + 1]
    return first_middle, last_tokens


def _format_academic(first_middle: List[str], last_tokens: List[str]) -> str:
    """Format the name in academic style: 'Last, First Middle'."""
    last = " ".join(_title_token(t) for t in last_tokens if t)
    first = " ".join(_title_token(t) for t in first_middle if t)
    return f"{last}, {first}".strip().strip(",")


def clean_author(name: str) -> str | None:
    """Clean and format author name to 'Last, First Middle' academic style.
    
    Handles:
    - Emails, ORCIDs, degrees
    - Footnote markers (*, †, ‡, digits)
    - Comma-separated forms
    - Multi-word surnames with particles
    """
    if not name:
        return None
    
    # Remove emails
    name = re.sub(r'\b[\w.+-]+@[\w.-]+\.\w+\b', '', name)
    # Remove ORCID URLs
    name = re.sub(r'\bhttps?://orcid\.org/\d{4}-\d{4}-\d{4}-\d{3}[0-9X]\b', '', name)
    # Remove degrees
    name = re.sub(r'\b(PhD|MSc|MD|BSc|DPhil|MA|MBA)\b', '', name, flags=re.IGNORECASE)
    # Remove marker symbols (*, daggers, section/pilcrow, etc.)
    name = re.sub(r'[\*\u2020\u2021\u00A7\u00B6\u2016]', '', name)
    # Remove numeric indices and footnote-like refs
    name = re.sub(r'\b\d+\b', '', name)
    name = re.sub(r'\(\s*[0-9a-zA-Z]+\s*\)', '', name)
    # Strip brackets
    name = name.translate(str.maketrans('', '', '[]{}'))
    # Normalize commas spacing
    name = re.sub(r'\s+,', ',', name)
    name = re.sub(r',\s+', ', ', name)
    # Collapse whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    
    if not name:
        return None
    
    # If already "Last, First" form, keep comma split; else split heuristically
    if "," in name:
        parts = [p.strip() for p in name.split(",", 1)]
        last_tokens = [t for t in parts[0].split() if t]
        first_middle = [t for t in parts[1].split() if t] if len(parts) > 1 else []
    else:
        toks = [t for t in name.split() if t]
        first_middle, last_tokens = _split_first_last(toks)
    
    # Filter stray single letters without period
    first_middle = [t for t in first_middle if not re.fullmatch(r'[A-Za-z]', t)]
    last_tokens = [t for t in last_tokens if not re.fullmatch(r'[A-Za-z]', t)]
    
    if not last_tokens:
        # Fallback: if everything was first names, just title-case and return
        simple = " ".join(_title_token(t) for t in first_middle)
        return simple or None
    
    formatted = _format_academic(first_middle, last_tokens)
    return formatted or None