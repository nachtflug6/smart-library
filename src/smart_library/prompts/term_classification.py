from __future__ import annotations
from typing import List, Dict

TAGS = [
    "model","method","algorithm","dataset","task","metric","concept","problem",
    "efficiency","accuracy","robustness","scalability","general-purpose","scientific",
    "engineering","data-driven","real-world","function","operator","structure","process",
    "static","dynamic","sequential","event-based",
]

CONTEXT_CLASSES = [
    "references","prose","title","abstract","caption","footnote",
]

def term_context_classification_prompt(items: List[Dict]) -> str:
    """
    Build user prompt for classifying each (term, context) with tags + context_class.
    Returns a single string to be used as the user message.
    """
    example = {
        "term": "diffusion model",
        "tags": ["model","scientific"],
        "context_class": "prose",
    }

    def _fmt_item(i: Dict) -> str:
        term = i.get("term","")
        ctx  = i.get("context","")
        return f"- term: {term}\n  context: {ctx}"

    items_block = "\n".join(_fmt_item(i) for i in items)

    return f"""You are classifying technical terms in their local text context.

For EACH term below, choose:
- tags: zero or more from this fixed list (no others, lowercase): {TAGS}
- context_class: exactly one of: {CONTEXT_CLASSES}

Guidelines:
- tags should reflect the role of the term in the provided context (e.g., model vs method vs dataset).
- Prefer few precise tags over many generic ones.
- If unsure, return an empty array for tags.
- context_class describes the surrounding text type.

Return STRICT JSON ONLY (an array of objects):
[
  {{
    "term": string,
    "tags": string[],
    "context_class": string
  }},
  ...
]

Example shape (values are illustrative only):
{example}

Items to classify:
{items_block}
"""