# filepath: /workspaces/smart-library/tests/test_term_classification_api_smoke.py
import json
import os
import random
from pathlib import Path
import pytest

from smart_library.extract.terms_classes import classify_term_contexts_batch
from smart_library.pipelines.base import get_llm_client
from smart_library.prompts.user_prompts import (
    term_context_classification_prompt,
    TERM_CONTEXT_TAGS,
    TERM_CONTEXT_CLASSES,
)

CTX = Path("data/jsonl/joins/terms_pages_context.jsonl")

ALLOWED_TAGS = set(TERM_CONTEXT_TAGS)
ALLOWED_CONTEXT_CLASSES = set(TERM_CONTEXT_CLASSES)

@pytest.mark.smoke
def test_single_api_classification_call(classify_n: int):
    assert CTX.exists(), f"Missing input file: {CTX}"
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set; skipping live API smoke test.")

    by_term = {}
    with CTX.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            ctx = obj.get("context")
            term = obj.get("term")
            if not ctx or not isinstance(term, str):
                continue
            by_term.setdefault(term, []).append(obj)

    assert by_term, "No rows with context available."
    rnd = random.Random(os.urandom(16))
    per_term_rows = [rnd.choice(rows) for rows in by_term.values()]
    actual_n = min(classify_n, len(per_term_rows))
    rows = rnd.sample(per_term_rows, actual_n)
    items = [{"term": r["term"], "context": r["context"]} for r in rows]

    prompt = term_context_classification_prompt(items)
    print(f"\n=== LLM CLASSIFICATION PROMPT ({actual_n} unique term(s)) ===\n")
    print(prompt)
    print("\n=== END PROMPT ===\n")

    client = get_llm_client(model="gpt-5-mini", api_key=api_key)
    parsed, reason = classify_term_contexts_batch(
        items, client, model="gpt-5-mini", temperature=0.2, debug=True
    )

    assert parsed is not None, f"LLM parse failed: {reason}"
    assert len(parsed) == actual_n, f"Expected {actual_n} objects, got {len(parsed)}"

    for i, obj in enumerate(parsed):
        assert obj.get("term") == items[i]["term"]
        tags = obj.get("tags", [])
        ctxc = obj.get("context_class")
        info = obj.get("information_content")
        assert isinstance(tags, list), "tags must be list"
        for t in tags:
            assert t in ALLOWED_TAGS, f"Unexpected tag: {t}"
        assert ctxc in ALLOWED_CONTEXT_CLASSES, f"Unexpected context_class: {ctxc}"
        assert isinstance(info, (int, float)), "information_content must be numeric"
        assert 0.0 <= float(info) <= 1.0, f"information_content out of range: {info}"

    print("=== LLM OUTPUT ===")
    for obj in parsed:
        print(json.dumps(obj, ensure_ascii=False, indent=2))
    print("=== END OUTPUT ===\n")