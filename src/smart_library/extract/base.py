"""Shared extraction utilities for LLM-based extraction."""

from __future__ import annotations
from typing import Dict, Any, List, Callable

from smart_library.llm.client import BaseLLMClient
from smart_library.utils.parsing import parse_structured_obj


def build_extraction_messages(
    system_prompt: str,
    user_prompt: str,
) -> List[Dict[str, str]]:
    """Build standard message structure for extraction."""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def prepare_llm_call_args(
    model: str,
    temperature: float = 1.0,
    enforce_json: bool = True,
) -> tuple[float | None, Dict[str, str] | None]:
    """Prepare temperature and response_format args for LLM call."""
    temp_arg = None if "gpt-5" in model.lower() else temperature
    response_format = {"type": "json_object"} if enforce_json else None
    return temp_arg, response_format


def extract_with_llm(
    text: str,
    client: BaseLLMClient,
    system_prompt: str,
    user_prompt_fn: Callable[[str], str],
    *,
    model: str = "gpt-5-mini",
    temperature: float = 1.0,
    enforce_json: bool = True,
    debug: bool = False,
) -> tuple[Dict[str, Any] | List[Any] | None, str]:
    """
    Generic LLM extraction with consistent error handling.
    
    Returns (data, reason) where data is parsed object or None.
    """
    if not text or not text.strip():
        return None, "empty_text"
    
    msgs = build_extraction_messages(system_prompt, user_prompt_fn(text))
    temp_arg, response_format = prepare_llm_call_args(model, temperature, enforce_json)

    raw = client.chat(
        model=model,
        messages=msgs,
        temperature=temp_arg,
        response_format=response_format,
    )
    
    if debug:
        print("RAW:", raw[:400])
    
    return parse_structured_obj(raw)


def extract_bulk_with_llm(
    batch_inputs: List[tuple[str, Any]],  # [(text, metadata), ...]
    client: BaseLLMClient,
    system_prompt: str,
    user_prompt_fn: Callable[[str], str],
    *,
    model: str = "gpt-5-mini",
    temperature: float = 1.0,
    max_workers: int = 6,
    enforce_json: bool = True,
) -> List[tuple[Any, str, str]]:
    """
    Generic bulk LLM extraction.
    
    Args:
        batch_inputs: List of (text, metadata) pairs where metadata will be returned with results
        
    Returns:
        List of (metadata, raw_response, reason) tuples
    """
    temp_arg, response_format = prepare_llm_call_args(model, temperature, enforce_json)

    batches: List[List[Dict[str, str]]] = []
    metas: List[Any] = []
    
    for text, meta in batch_inputs:
        if not text or not text.strip():
            continue
        batches.append(build_extraction_messages(system_prompt, user_prompt_fn(text)))
        metas.append(meta)

    if not batches:
        return []

    raws = client.chat_concurrent(
        model=model,
        list_of_messages=batches,
        temperature=temp_arg,
        response_format=response_format,
        max_workers=max_workers,
        apply_rate_limit=True,
    )

    return [(meta, raw, "") for meta, raw in zip(metas, raws)]