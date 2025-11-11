import json
import os
from pathlib import Path
import pytest

from smart_library.pipelines.term_classification import llm_term_context_classify
from smart_library.prompts.user_prompts import TERM_CONTEXT_TAGS, TERM_CONTEXT_CLASSES

IN_PATH = Path("data/jsonl/joins/terms_pages_context.jsonl")
OUT_PATH = Path("data/jsonl/joins/terms_pages_classified_smoke.jsonl")

ALLOWED_TAGS = set(TERM_CONTEXT_TAGS)
ALLOWED_CONTEXT_CLASSES = set(TERM_CONTEXT_CLASSES)

@pytest.mark.smoke
def test_pipeline_classify_file_io():
    """
    Run the full classification pipeline on a small subset (5 terms),
    validate output file format and field presence.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set; skipping pipeline smoke test.")

    assert IN_PATH.exists(), f"Missing input: {IN_PATH}"

    # Create a temporary subset input with 5 rows
    temp_in = Path("data/jsonl/joins/terms_pages_context_smoke.jsonl")
    temp_in.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    with IN_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            if obj.get("context"):
                rows.append(obj)
                if len(rows) >= 5:
                    break

    assert rows, "Not enough context rows for smoke test."

    with temp_in.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Temporarily override IN_PATH in the pipeline module
    import smart_library.pipelines.term_classification as tc_module
    orig_in = tc_module.IN_PATH
    orig_out = tc_module.OUT_PATH
    tc_module.IN_PATH = temp_in
    tc_module.OUT_PATH = OUT_PATH

    try:
        written = llm_term_context_classify(
            model="gpt-5-mini",
            api_key=api_key,
            temperature=0.2,
            batch_size=5,
            include_unfound=True,
            debug=True,
        )
        assert written == len(rows), f"Expected {len(rows)} written, got {written}"
        assert OUT_PATH.exists(), "Output file not created."

        # Validate output structure
        out_rows = []
        with OUT_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    out_rows.append(json.loads(line))

        assert len(out_rows) == len(rows), "Output row count mismatch."

        print("\n=== PIPELINE OUTPUT (file I/O + API) ===\n")
        for row in out_rows:
            # Check required output fields
            assert "term" in row, "Missing field: term"
            assert "tags" in row, "Missing field: tags"
            assert "context_class" in row, "Missing field: context_class"
            assert "information_content" in row, "Missing field: information_content"

            tags = row["tags"]
            ctxc = row["context_class"]
            info = row["information_content"]

            assert isinstance(tags, list), "tags must be list"
            for t in tags:
                assert t in ALLOWED_TAGS, f"Unexpected tag: {t}"
            assert ctxc in ALLOWED_CONTEXT_CLASSES, f"Unexpected context_class: {ctxc}"
            assert isinstance(info, (int, float)), "information_content must be numeric"
            assert 0.0 <= float(info) <= 1.0, f"information_content out of range: {info}"

            # Check that original fields are preserved
            assert "document_id" in row, "Missing preserved field: document_id"
            assert "page" in row, "Missing preserved field: page"
            assert "context" in row, "Missing preserved field: context"

            print(json.dumps(row, ensure_ascii=False, indent=2))
            print()

        print("=== END PIPELINE OUTPUT ===\n")

    finally:
        # Restore original paths
        tc_module.IN_PATH = orig_in
        tc_module.OUT_PATH = orig_out

        # Cleanup temporary files
        if temp_in.exists():
            temp_in.unlink()
        if OUT_PATH.exists():
            OUT_PATH.unlink()