"""Lenient parsing utilities for LLM outputs."""
import json
import re
import ast
from typing import Dict, Any, List


def parse_structured_obj(raw: str) -> tuple[Dict[str, Any] | List[Any] | None, str]:
    """Leniently parse LLM output into a JSON-like object or array.
    
    Returns (obj, reason). Accepts JSON objects, arrays, code-fenced JSON, Python literals.
    """
    if not raw or not raw.strip():
        return None, "empty_output"
    s = raw.strip()

    # Strip code fences
    m = re.match(r"^```(?:json|JSON)?\s*(.*?)\s*```$", s, re.DOTALL)
    if m:
        s = m.group(1).strip()

    # Try strict JSON (both objects and arrays)
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return obj, "json_ok"
        if isinstance(obj, list):
            return obj, "json_array"  # <-- Accept arrays directly
    except Exception:
        pass

    # Try Python literal
    try:
        obj = ast.literal_eval(s)
        if isinstance(obj, dict):
            return obj, "python_literal_dict"
        if isinstance(obj, list):
            return obj, "python_literal_array"  # <-- Accept arrays directly
    except Exception:
        pass

    # Salvage first {...} or [...] block
    for pattern, tag_obj, tag_arr in [
        (r'\{.*\}', "json_salvaged_obj", "json_salvaged_array"),
        (r'\[.*\]', "json_salvaged_array", "json_salvaged_array"),
    ]:
        m = re.search(pattern, s, re.DOTALL)
        if not m:
            continue
        blk = m.group(0)
        blk = re.sub(r",\s*([}\]])", r"\1", blk)  # Remove trailing commas

        for parser, tag_prefix in ((json.loads, "json_salvaged"), (ast.literal_eval, "python_salvaged")):
            try:
                obj = parser(blk)
                if isinstance(obj, dict):
                    return obj, tag_obj
                if isinstance(obj, list):
                    return obj, tag_arr
            except Exception:
                continue

    return None, "unparseable"