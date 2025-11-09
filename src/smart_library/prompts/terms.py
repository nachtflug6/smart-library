# smart_library/prompts/terms.py

def extract_terms_prompt(text: str) -> str:
    return f"""
Extract important technical terms from the following text.
Return JSON:
{{
  "terms": [
    {{"term": "...", "description": "..."}},
    ...
  ]
}}

Only include terms that appear explicitly in the text.

TEXT:
{text}
""".strip()
