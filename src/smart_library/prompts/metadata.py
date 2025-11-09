# smart_library/prompts/metadata.py

def metadata_extraction_prompt(text: str) -> str:
    return f"""
Extract the metadata from the following research paper text.

Return strict JSON with:
- "title"
- "authors"
- "venue"
- "year"
- "doi" (null if missing)

TEXT:
{text}
""".strip()
