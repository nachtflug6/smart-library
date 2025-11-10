def deterministic_extraction_prompt() -> str:
    return (
        "You are a deterministic metadata extractor.\n"
        "- Do not hallucinate.\n"
        "- Use null for uncertain or missing fields.\n"
        "- When JSON is requested, return only valid JSON with no extra text.\n"
    )
