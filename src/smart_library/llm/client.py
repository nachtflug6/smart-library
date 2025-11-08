"""
Unified LLM interface (sync + concurrent), backend: OpenAI.
Generic input/output. No forced schema. No model-specific code outside helpers.
"""

from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Dict, Any
import logging

from openai import OpenAI

logger = logging.getLogger(__name__)


# --------------------------
# Helpers for model quirks
# --------------------------

def _max_tokens_kwargs(model: str, max_output_tokens: int | None) -> dict:
    m = model.lower()
    if "gpt-5" in m or m.endswith("-nano"):
        return {}
    return {"max_tokens": max_output_tokens} if max_output_tokens else {}


def _temperature_kwargs(model: str, temperature: float) -> dict:
    m = model.lower()
    if "gpt-5" in m or m.endswith("-nano"):
        return {}
    return {"temperature": temperature}


# --------------------------
# Core API wrapper
# --------------------------

class LLMClient:
    """
    Generic interface for LLM calls (chat + concurrency) with OpenAI backend.
    You can later subclass or swap out the backend without touching call sites.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key)

    def chat(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        *,
        max_output_tokens: int | None = None,
        temperature: float = 0.0,
        response_format: Optional[dict] = None,
    ) -> str:
        """Generic chat call. Perfect for any prompt/format."""

        kwargs = {}
        kwargs.update(_max_tokens_kwargs(model, max_output_tokens))
        kwargs.update(_temperature_kwargs(model, temperature))

        # GPT-5 models: disable strict JSON mode automatically
        if "gpt-5" in model.lower() and response_format is None:
            response_format = {"type": "text"}

        if response_format:
            kwargs["response_format"] = response_format

        resp = self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs,
        )

        return (resp.choices[0].message.content or "").strip()

    # --------------------------
    # Concurrent version
    # --------------------------

    def chat_concurrent(
        self,
        model: str,
        list_of_messages: List[List[Dict[str, Any]]],
        *,
        max_output_tokens: int | None = None,
        temperature: float = 0.0,
        max_workers: int = 6,
        response_format: Optional[dict] = None,
    ) -> List[str]:
        """Run many chat calls concurrently. Order is preserved."""

        def _one(i: int, msgs: List[Dict[str, Any]]):
            try:
                text = self.chat(
                    model=model,
                    messages=msgs,
                    max_output_tokens=max_output_tokens,
                    temperature=temperature,
                    response_format=response_format,
                )
                return i, text
            except Exception as e:
                logger.error(f"Concurrent task {i} failed: {e}")
                return i, ""

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            future_map = {
                pool.submit(_one, i, msgs): i
                for i, msgs in enumerate(list_of_messages)
            }

            for fut in as_completed(future_map):
                try:
                    results.append(fut.result())
                except Exception as e:
                    idx = future_map[fut]
                    logger.error(f"Future {idx} exception: {e}")
                    results.append((idx, ""))

        results.sort(key=lambda x: x[0])
        return [r for _, r in results]
