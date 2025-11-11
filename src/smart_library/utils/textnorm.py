from __future__ import annotations

def normalize_term(term: str) -> str:
    # lowercase
    term = (term or "").lower()
    # strip whitespace, collapse multiple spaces
    term = " ".join(term.split())
    # strip common punctuation
    chars = "()[]{}:,.;"
    term = term.strip(chars)
    # remove extraction markup
    term = term.replace("term:", "").replace("[term:", "").replace("]", "")
    # cleanup linebreaks + hyphenation artifacts
    term = term.replace("\n", " ")
    term = term.replace("- ", "-")
    term = term.replace(" -", "-")
    # safe plural removal
    if term.endswith("s") and not term.endswith("ss"):
        term = term[:-1]
    return term

def normalize_text_window(text: str) -> str:
    # light-weight cleanup for context windows
    s = (text or "").lower()
    s = " ".join(s.split())          # collapse whitespace
    s = s.replace("\n", " ")
    s = s.replace("- ", "-").replace(" -", "-")
    return s.strip()