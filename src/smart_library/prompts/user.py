# smart_library/prompts/metadata.py

def metadata(text: str) -> str:
    return f"""
You are an expert assistant for extracting bibliographic metadata from research paper texts.
Extract the metadata from the following research paper text.

Return strict JSON with these fields (use null if not found or unsure):
- "title": str | null
- "authors": List[str] | null
- "venue": str | null
- "year": str | null
- "doi": str | null
- "keywords": List[str] | null

TEXT:
{text}
""".strip()
