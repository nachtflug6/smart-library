import json
import random
from pathlib import Path
import pytest

CTX = Path("data/jsonl/joins/terms_pages_context.jsonl")
OUT = Path("data/jsonl/joins/terms_pages_classified.jsonl")

TAGS = {
    "model","method","algorithm","dataset","task","metric","concept","problem",
    "efficiency","accuracy","robustness","scalability","general-purpose","scientific",
    "engineering","data-driven","real-world","function","operator","structure","process",
    "static","dynamic","sequential","event-based"
}
CONTEXT_CLASSES = {"references","prose","title","abstract","caption","footnote"}

@pytest.mark.smoke
def test_term_classification_output_structure():
    assert CTX.exists(), f"Context input file missing: {CTX}"
    assert OUT.exists(), (
        f"Classification output file missing: {OUT}. "
        "Run: python src/smart_library/cli/main.py terms-classify"
    )

    rows = [json.loads(l) for l in OUT.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert rows, (
        f"{OUT} is empty. Run classification first: "
        "python src/smart_library/cli/main.py terms-classify"
    )

    sample = random.sample(rows, min(20, len(rows)))
    issues = []
    for i, r in enumerate(sample, 1):
        term = r.get("term")
        tags = r.get("tags")
        context_class = r.get("context_class")
        if not isinstance(term, str):
            issues.append(f"{i}: term not string")
        if not isinstance(tags, list):
            issues.append(f"{i}: tags not list")
        else:
            for t in tags:
                if t not in TAGS:
                    issues.append(f"{i}: unexpected tag {t!r}")
        if context_class not in CONTEXT_CLASSES:
            issues.append(f"{i}: unexpected context_class {context_class!r}")
        for req in ("document_id","page","context"):
            if req not in r:
                issues.append(f"{i}: missing field {req}")

    if issues:
        pytest.fail("Classification output issues:\n" + "\n".join(issues))