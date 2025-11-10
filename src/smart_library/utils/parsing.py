"""Lenient parsing utilities for LLM outputs."""
import json
import re
import ast
from typing import Dict, Any


def parse_structured_obj(raw: str) -> tuple[Dict[str, Any] | None, str]:
    """Leniently parse LLM output into a JSON-like object.
    
    Returns (obj, reason). Accepts JSON, code-fenced JSON, Python literals, arrays.
    """
    if not raw or not raw.strip():
        return None, "empty_output"
    s = raw.strip()

    # Strip code fences
    m = re.match(r"^```(?:json|JSON)?\s*(.*?)\s*```$", s, re.DOTALL)
    if m:
        s = m.group(1).strip()

    # Try strict JSON
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return obj, "json_ok"
        if isinstance(obj, list) and obj and isinstance(obj[0], dict):
            return obj[0], "json_array_first_object"
    except Exception:
        pass

    # Try Python literal
    try:
        obj = ast.literal_eval(s)
        if isinstance(obj, dict):
            return obj, "python_literal_dict"
        if isinstance(obj, list) and obj and isinstance(obj[0], dict):
            return obj[0], "python_literal_array_first_object"
    except Exception:
        pass

    # Salvage first {...} block
    start, end = s.find("{"), s.rfind("}")
    if start != -1 and end != -1 and end > start:
        blk = s[start : end + 1]
        blk = re.sub(r",\s*([}\]])", r"\1", blk)

        for parser, tag in ((json.loads, "json_salvaged"), (ast.literal_eval, "python_salvaged")):
            try:
                obj = parser(blk)
                if isinstance(obj, dict):
                    return obj, tag
                if isinstance(obj, list) and obj and isinstance(obj[0], dict):
                    return obj[0], tag + "_array"
            except Exception:
                continue

    return None, "unparseable"