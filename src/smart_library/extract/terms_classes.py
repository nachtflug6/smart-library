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
    workers: int = 1,          # NEW
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

    if debug:
        # Force single batch in debug
        rows = rows[:batch_size]
        workers = 1
        if debug:
            print(f"[DEBUG] limiting rows to {len(rows)} (single batch)")
    # Build batches
    batches = []
    for i in range(0, len(rows), batch_size):
        batch_rows = rows[i:i+batch_size]
        items = [{"term": r.get("term",""), "context": r.get("context","") or ""} for r in batch_rows]
        user_msg = term_context_classification_prompt(items)
        messages = [
            {"role": "system", "content": "You are a precise text classifier. Return ONLY a strict JSON array."},
            {"role": "user", "content": user_msg},
        ]
        batches.append((i // batch_size, batch_rows, messages))
    # Sequential path
    if workers <= 1 or len(batches) == 1:
        for idx, batch_rows, messages in batches:
            resp = client.chat(messages=messages, model=model, temperature=temperature)
            text = resp if isinstance(resp, str) else getattr(resp, "content", str(resp))
            parsed, reason = _coerce_json_array(text)
            if debug and reason:
                print(f"[DEBUG] batch {idx} parse issue: {reason}")
            out.extend(_merge_batch(batch_rows, parsed, debug))
        return out
    # Concurrent path
    all_messages = [m for _, _, m in batches]
    if debug:
        print(f"[DEBUG] running {len(batches)} batches concurrently (workers={workers})")
    responses = client.chat_concurrent(
        model=model,
        list_of_messages=all_messages,
        temperature=temperature,
        max_workers=workers,
    )
    for (idx, batch_rows, _), resp in zip(batches, responses):
        text = resp if isinstance(resp, str) else getattr(resp, "content", str(resp))
        parsed, reason = _coerce_json_array(text)
        if debug and reason:
            print(f"[DEBUG] batch {idx} parse issue: {reason}")
        out.extend(_merge_batch(batch_rows, parsed, debug))
    return out

def _merge_batch(batch_rows: List[Dict[str, Any]], parsed: List[Dict[str, Any]] | None, debug: bool) -> List[Dict[str, Any]]:
    allowed_tags = set(TERM_CONTEXT_TAGS)
    allowed_classes = set(TERM_CONTEXT_CLASSES)
    if not parsed:
        if debug:
            print("[DEBUG] fallback defaults for batch")
        out_rows=[]
        for r in batch_rows:
            o=dict(r)
            o["tags"]=[]
            o["context_class"]="prose"
            o["information_content"]=0.0
            out_rows.append(o)
        return out_rows
    out_rows=[]
    for idx,r in enumerate(batch_rows):
        o=dict(r)
        cls = parsed[idx] if idx < len(parsed) else {}
        tags = cls.get("tags", []) if isinstance(cls, dict) else []
        ctxc = cls.get("context_class", "prose") if isinstance(cls, dict) else "prose"
        info = cls.get("information_content", 0)
        if isinstance(info,(int,float)): info=float(info)
        elif isinstance(info,str):
            try: info=float(info.strip())
            except: info=0.0
        else: info=0.0
        if info<0: info=0.0
        if info>1: info=1.0
        if not isinstance(tags,list): tags=[]
        o["tags"]=[t for t in tags if isinstance(t,str) and t in allowed_tags]
        o["context_class"]=ctxc if ctxc in allowed_classes else "prose"
        o["information_content"]=info
        out_rows.append(o)
    return out_rows