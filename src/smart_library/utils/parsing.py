"""Lenient parsing utilities for LLM outputs."""
import json
import re
import ast
from typing import Dict, Any, List, Tuple


def parse_structured_obj(raw: str, *, strict_json: bool = False) -> tuple[Dict[str, Any] | List[Any] | None, str]:
    """Leniently parse LLM output into a JSON-like object or array.

    Returns (obj, reason).

    Modes:
    - strict_json=True: accept only strict JSON (objects/arrays). No Python literal or salvage.
    - strict_json=False (default): accept strict JSON, Python literals, and salvaged inner blocks.
    """
    if not raw or not raw.strip():
        return None, "empty_output"

    s = raw.strip()

    # Strip code fences
    m = re.match(r"^```(?:json|JSON)?\s*(.*?)\s*```$", s, re.DOTALL)
    if m:
        s = m.group(1).strip()

    # Strict JSON path
    if strict_json:
        try:
            obj = json.loads(s)
            if isinstance(obj, dict):
                return obj, "json_ok"
            if isinstance(obj, list):
                return obj, "json_array"
        except Exception:
            return None, "json_invalid"

    # Try strict JSON first (lenient mode still prefers JSON)
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return obj, "json_ok"
        if isinstance(obj, list):
            return obj, "json_array"
    except Exception:
        pass

    # Try Python literal (lenient acceptance)
    try:
        obj = ast.literal_eval(s)
        if isinstance(obj, dict):
            return obj, "python_literal_dict"
        if isinstance(obj, list):
            return obj, "python_literal_array"
    except Exception:
        pass

    # Salvage first {...} or [...] block (lenient acceptance)
    for pattern, tag_obj, tag_arr in [
        (r"\{.*\}", "json_salvaged_obj", "json_salvaged_array"),
        (r"\[.*\]", "json_salvaged_array", "json_salvaged_array"),
    ]:
        m = re.search(pattern, s, re.DOTALL)
        if not m:
            continue
        blk = m.group(0)
        # Remove trailing commas immediately before closing delimiters
        blk = re.sub(r",\s*([}\]])", r"\1", blk)

        for parser, tag_obj2, tag_arr2 in (
            (json.loads, tag_obj, tag_arr),
            (ast.literal_eval, "python_salvaged_dict", "python_salvaged_array"),
        ):
            try:
                obj = parser(blk)
                if isinstance(obj, dict):
                    return obj, tag_obj2
                if isinstance(obj, list):
                    return obj, tag_arr2
            except Exception:
                continue

    return None, "unparseable"