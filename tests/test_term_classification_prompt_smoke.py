import json
import random
from pathlib import Path
import pytest

from smart_library.prompts.user_prompts import term_context_classification_prompt

CTX = Path("data/jsonl/joins/terms_pages_context.jsonl")

@pytest.mark.smoke
def test_term_classification_prompt_smoke():
    assert CTX.exists(), f"Missing input context file: {CTX}"
    rows = []
    with CTX.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                obj = json.loads(line)
                if obj.get("context_status") == "found" and obj.get("context"):
                    rows.append(obj)
    assert rows, "No rows with found context to build prompt."

    sample = random.sample(rows, min(20, len(rows)))
    items = [{"term": r.get("term", ""), "context": r.get("context", "")} for r in sample]

    prompt = term_context_classification_prompt(items)

    print("\n=== TERM CONTEXT CLASSIFICATION PROMPT (SMOKE) ===\n")
    print(prompt)
    print("\n=== END PROMPT ===\n")
    assert "tags" in prompt.lower()
    assert "context_class" in prompt.lower()
    assert len(prompt) > 200