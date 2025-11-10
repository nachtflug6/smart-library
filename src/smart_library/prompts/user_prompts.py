# smart_library/prompts/metadata.py

def metadata_extraction_prompt(text: str, expected_format: str | None = None) -> str:
    """
    Relaxed prompt: model may return any subset of target fields.
    We will fill missing ones to null downstream.
    """
    fmt = expected_format or """
{
  "title": string | null,
  "authors": string[] | null,
  "venue": string | null,
  "year": integer | null,
  "doi": string | null,
  "abstract": string | null,
  "keywords": string[] | null,
  "arxiv_id": string | null,
  "url": string | null
}
""".strip()

    return f"""Extract bibliographic metadata from the paper TEXT.

Return STRICT JSON matching exactly this shape (no extra keys, no markdown):
{fmt}

Author formatting rules:
- Output each author as: Last, First Middle (academic format).
- If source is "First Middle Last", convert to "Last, First Middle".
- Preserve multi-word surnames and particles (e.g., "De Brouwer" -> "De Brouwer, Edward").
- Keep initials with periods (e.g., "J. B. Oliva" -> "Oliva, J. B.").
- Remove emails, ORCIDs, degrees, and markers (*, †, ‡, digits, indices).
- Collapse spaces; drop empty results; preserve original author order.

Other rules:
- Use null for missing or uncertain fields.
- year: integer (e.g., 2019).
- keywords: short lowercase phrases.
- Output ONLY the JSON object.

TEXT:
{text}
"""


def term_extraction_prompt(text: str) -> str:
    """
    Extract technical terms from a single page of text.
    Returns a JSON array of term strings.
    """
    return f"""Extract specialized TERMS from the TEXT.

Return a JSON array of lowercase unique terms (max 30 terms):
["term1", "term2", "term3"]

Goal: extract non-generic, content terms (be broad; when unsure, INCLUDE):
- concepts, systems, components
- technical jargon, methods, theories
- applications, domains, real-world problems
- datasets/benchmarks/tasks (keep official names, even if they include years)
- acronyms and multi-word phrases

Exclude (document metadata & noise):
- people (researchers/authors)
- publication/venue metadata (venues, conferences, years used only as citation info, affiliations)
- section/figure/table/page refs
- formatting artifacts, markdown, footnotes, equations/variables/symbols unless they are named concepts

Rules:
- lowercase everything
- preserve multi-word phrases
- keep acronyms as written

TEXT:
{text}
"""
