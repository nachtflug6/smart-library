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


# EXPORT shared constants for term-context classification
TERM_CONTEXT_TAGS = ['task',
 'objective',
 'challenge',
 'dataset',
 'feature',
 'label',
 'model',
 'method',
 'architecture',
 'observation',
 'application',
 'metric',
 'example',
 'concept']

TERM_CONTEXT_CLASSES = [
    "title","heading","prose","list","footnote","table","math","code","caption","reference"
]

def term_context_classification_prompt(items: list[dict]) -> str:
    """
    Classify each (term, context) with:
      - tags (list from TERM_CONTEXT_TAGS)
      - context_class (one from TERM_CONTEXT_CLASSES)
      - information_content (float in [0,1]; 0 = none, 1 = highly informative)
    """
    TAGS = TERM_CONTEXT_TAGS
    CONTEXT_CLASSES = TERM_CONTEXT_CLASSES

    example = {
        "term": "diffusion model",
        "tags": ["model","concept"],
        "context_class": "prose",
        "information_content": 0.85
    }

    def _fmt_item(i: dict) -> str:
        term = i.get("term","")
        ctx  = i.get("context","")
        return f"- term: {term}\n  context: {ctx}"

    items_block = "\n".join(_fmt_item(i) for i in items)

    return f"""You are classifying technical terms in their local text context.

For EACH term below, choose ONLY:
- tags: zero, one or multiple from this fixed list (no others): {TAGS}
- context_class: exactly one from: {CONTEXT_CLASSES}
- information_content: a decimal number in [0,1]

information_content scale (choose a value; may use one decimal place):
  0.0  = trivial / generic mention / out-of-context (no added knowledge)
  0.2  = minimal hint
  0.4  = some detail
  0.6  = clear descriptive / functional info
  0.8  = rich explanation / relationships / properties
  1.0  = highly informative, definition-like or multi-faceted insight

Guidelines:
- Never invent tags outside the list. If none fit, return [].
- Prefer the most specific semantic/functional role.
- context_class reflects structural region.
- If unsure on information_content, bias lower.
- Use standard JSON number (no quotes).

Return STRICT JSON ONLY (array of objects). Each object MUST have:
  "term": string,
  "tags": string[],
  "context_class": string,
  "information_content": number (0 <= value <= 1)

Example shape (illustrative):
{example}

Items to classify:
{items_block}
"""