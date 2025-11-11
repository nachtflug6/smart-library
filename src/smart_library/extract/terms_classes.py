"""Core term-context classification logic."""

from __future__ import annotations
from typing import List, Dict, Any, Tuple
import json
import re

from smart_library.llm.client import BaseLLMClient
from smart_library.prompts.user_prompts import (
    term_context_classification_prompt,
    TERM_CONTEXT_TAGS,
    TERM_CONTEXT_CLASSES,
)

def _coerce_json_array(text: str) -> Tuple[List[Dict[str, Any]] | None, str | None]:
    """
    Try to parse a JSON array from LLM output; return (data, reason_if_error).
    """
    raw = (text or "").strip()
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data, None
    except Exception as e:
        reason = f"json.loads failed: {e}"
    else:
        reason = "not a list"

    # Fallback: extract the outermost [...] block
    m = re.search(r"\[.*\]", raw, re.DOTALL)
    if not m:
        return None, reason or "no array block found"
    frag = m.group(0)
    try:
        data = json.loads(frag)
        if isinstance(data, list):
            return data, None
        return None, "fragment not a list"
    except Exception as e:
        return None, f"fragment parse failed: {e}"

def classify_term_contexts_batch(
    items: List[Dict[str, Any]],
    client: BaseLLMClient,
    *,
    model: str = "gpt-5-mini",
    temperature: float = 0.2,
    debug: bool = False,
) -> Tuple[List[Dict[str, Any]] | None, str | None]:
    """
    Classify a batch of items [{term, context}, ...] with one LLM call.
    Returns (parsed_list_or_none, reason_if_error).
    """
    user_msg = term_context_classification_prompt(items)
    messages = [
        {"role": "system", "content": "You are a precise text classifier. Return ONLY a strict JSON array."},
        {"role": "user", "content": user_msg},
    ]

    resp = client.chat(messages=messages, model=model, temperature=temperature)
    text = resp if isinstance(resp, str) else getattr(resp, "content", str(resp))
    parsed, reason = _coerce_json_array(text)

    if debug:
        print("[classify batch] items:", len(items))
        if reason:
            print("[classify batch] parse issue:", reason)
            print("[classify batch] raw head:", text[:400])

    return parsed, reason

def classify_term_contexts_bulk(
    rows: List[Dict[str, Any]],
    client: BaseLLMClient,
    *,
    model: str = "gpt-5-mini",
    temperature: float = 0.2,
    batch_size: int = 20,
    debug: bool = False,
) -> List[Dict[str, Any]]:
    """
    Bulk classification.
    - rows: input rows containing at least term, context; other fields are preserved.
    - Returns rows with added fields: tags (list[str]), context_class (str).
    """
    out: List[Dict[str, Any]] = []
    if not rows:
        return out
    allowed_tags = set(TERM_CONTEXT_TAGS)
    allowed_classes = set(TERM_CONTEXT_CLASSES)

    # Chunk rows into batches
    for i in range(0, len(rows), batch_size):
        batch_rows = rows[i : i + batch_size]
        items = [{"term": r.get("term", ""), "context": r.get("context", "") or ""} for r in batch_rows]

        parsed, reason = classify_term_contexts_batch(
            items, client, model=model, temperature=temperature, debug=debug
        )

        if not parsed:
            # Fallback: emit defaults for this batch
            if debug:
                print(f"[classify bulk] batch {i//batch_size}: fallback due to {reason}")
            for r in batch_rows:
                o = dict(r)
                o["tags"] = []
                o["context_class"] = "prose"
                out.append(o)
            continue

        # Merge back in order; if lengths mismatch, align sequentially.
        for idx, r in enumerate(batch_rows):
            o = dict(r)
            cls = parsed[idx] if idx < len(parsed) else {}
            tags = cls.get("tags", []) if isinstance(cls, dict) else []
            ctxc = cls.get("context_class", "prose") if isinstance(cls, dict) else "prose"
            info = cls.get("information_content", 0) if isinstance(cls, dict) else 0
            # Normalize information_content to float in [0,1]
            if isinstance(info, (int, float)):
                info = float(info)
            elif isinstance(info, str):
                try:
                    info = float(info.strip())
                except Exception:
                    info = 0.0
            else:
                info = 0.0
            if info < 0: info = 0.0
            if info > 1: info = 1.0
            # Filter to allowed sets
            o["tags"] = [t for t in tags if isinstance(t, str) and t in allowed_tags]
            o["context_class"] = ctxc if ctxc in allowed_classes else "prose"
            o["information_content"] = info
            out.append(o)

    return out