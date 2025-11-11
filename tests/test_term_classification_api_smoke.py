import json
import os
from pathlib import Path
import pytest

from smart_library.extract.terms_classes import classify_term_contexts_batch
from smart_library.pipelines.base import get_llm_client

CTX = Path("data/jsonl/joins/terms_pages_context.jsonl")

ALLOWED_TAGS = {
    "model","method","algorithm","dataset","task","metric","concept","problem",
    "efficiency","accuracy","robustness","scalability","general-purpose","scientific",
    "engineering","data-driven","real-world","function","operator","structure","process",
    "static","dynamic","sequential","event-based",
}
ALLOWED_CONTEXT_CLASSES = {"references","prose","title","abstract","caption","footnote"}

@pytest.mark.smoke
def test_single_api_classification_call():
    assert CTX.exists(), f"Missing input file: {CTX}"

    # Require a real API key; skip if not provided
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or "your_key" in api_key:
        pytest.skip("OPENAI_API_KEY not set; skipping live API smoke test.")

    rows = []
    with CTX.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                obj = json.loads(line)
                if obj.get("context"):  # need some context text
                    rows.append(obj)
            if len(rows) >= 3:
                break
    assert rows, "No rows with context available to classify."

    items = [{"term": r["term"], "context": r["context"]} for r in rows]

    client = get_llm_client(model="gpt-5-mini", api_key=api_key)
    parsed, reason = classify_term_contexts_batch(
        items,
        client,
        model="gpt-5-mini",
        temperature=0.2,
        debug=True,
    )
    assert parsed is not None, f"LLM parse failed: {reason}"
    assert len(parsed) == len(items), f"Mismatch count parsed={len(parsed)} expected={len(items)}"

    for i, obj in enumerate(parsed):
        assert obj.get("term") == items[i]["term"]
        tags = obj.get("tags", [])
        ctxc = obj.get("context_class")
        assert isinstance(tags, list)
        for t in tags:
            assert t in ALLOWED_TAGS, f"Unexpected tag: {t}"
        assert ctxc in ALLOWED_CONTEXT_CLASSES, f"Unexpected context_class: {ctxc}"

    print("\nAPI classification sample:")
    for obj in parsed:
        print(f"- {obj['term']}: tags={obj.get('tags')} context_class={obj.get('context_class')}")