"""
OpenAI-specific implementation of BaseLLMClient with adaptive parameter handling.
Default behavior assumes gpt-5 family quirks; 4o/4* models get legacy params.
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
import logging
import os
import json

from openai import OpenAI

from smart_library.llm.client import BaseLLMClient
from smart_library.llm.rates import get_model_limits, estimate_message_tokens

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _is_4o(model: str) -> bool:
    m = model.lower()
    return ("gpt-4" in m) or ("4o" in m)


class OpenAIClient(BaseLLMClient):
    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        default_model: Optional[str] = None,
        default_rpm: int | None = None,
        default_tpm: int | None = None,
    ):
        super().__init__(
            default_model=default_model,
            default_rpm=default_rpm,
            default_tpm=default_tpm,
            limits_provider=get_model_limits,
            token_estimator=estimate_message_tokens,
        )
        self.client = OpenAI(api_key=api_key)

    def _call_api(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        *,
        max_output_tokens: int | None = None,
        temperature: float | None = 1.0,
        response_format: Optional[dict] = None,
    ) -> str:
        """
        Defaults to gpt-5 behavior:
          - Uses max_completion_tokens
          - Omits temperature
          - Ignores response_format (JSON mode)
        For 4o/gpt-4 models:
          - Uses max_tokens
          - Includes temperature if provided
          - Allows response_format
        On 400s, adapt by swapping/removing offending params.
        """
        is4o = _is_4o(model)

        kwargs: Dict[str, Any] = {"model": model, "messages": messages}

        # Token parameter
        token_param = "max_tokens" if is4o else "max_completion_tokens"
        if max_output_tokens is not None:
            kwargs[token_param] = max_output_tokens

        # Temperature
        if is4o:
            if temperature is not None:
                kwargs["temperature"] = temperature
        # else: omit for gpt-5 family (defaults to model’s allowed setting)

        # Response format
        if is4o and response_format is not None:
            kwargs["response_format"] = response_format
        # else: omit for gpt-5 family

        def _attempt(k: Dict[str, Any]):
            return self.client.chat.completions.create(**k)

        try:
            resp = _attempt(kwargs)
        except Exception as e:
            msg = str(e).lower()

            # Swap token param if rejected
            if "unsupported parameter" in msg and "max_tokens" in msg and "max_tokens" in kwargs:
                val = kwargs.pop("max_tokens")
                kwargs["max_completion_tokens"] = val
                resp = _attempt(kwargs)
            elif "unsupported parameter" in msg and "max_completion_tokens" in msg and "max_completion_tokens" in kwargs:
                val = kwargs.pop("max_completion_tokens")
                kwargs["max_tokens"] = val
                resp = _attempt(kwargs)
            # Drop temperature if rejected
            elif "unsupported value" in msg and "temperature" in msg and "temperature" in kwargs:
                kwargs.pop("temperature", None)
                resp = _attempt(kwargs)
            # Drop response_format if rejected
            elif "unsupported parameter" in msg and "response_format" in msg and "response_format" in kwargs:
                kwargs.pop("response_format", None)
                resp = _attempt(kwargs)
            else:
                raise

        # Extract content (try parsed if content is empty)
        try:
            content = (resp.choices[0].message.content or "").strip()
        except Exception:
            content = ""

        if not content:
            # Some newer models may return parsed structured output
            try:
                parsed = getattr(resp.choices[0].message, "parsed", None)
                if parsed is not None:
                    try:
                        # parsed can be dict-like
                        content = json.dumps(parsed, ensure_ascii=False)
                    except Exception:
                        content = str(parsed)
            except Exception:
                pass

        return content or ""


if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set. Skipping smoke test.")
        raise SystemExit(0)

    client = OpenAIClient(api_key=api_key, default_model="gpt-5-mini")

    model = "gpt-5-mini"
    tests = [
        {
            "label": "T1 simple word",
            "messages": [{"role": "user", "content": "Say Hello"}],
            "max_output_tokens": 64,
        },
        {
            "label": "T2 tiny JSON",
            "messages": [
                {"role": "system", "content": "Return only valid JSON. No extra text."},
                {"role": "user", "content": 'Give me {"ok": true} exactly.'},
            ],
            "max_output_tokens": 256,
        },
        {
            "label": "T3 metadata subset",
            "messages": [
                {"role": "system", "content": "Return JSON only."},
                {"role": "user", "content": "Title: Example Research\nAuthors: Alice Smith, Bob Lee\nReturn JSON with title, authors."},
            ],
            "max_output_tokens": 800,
        },
    ]

    for t in tests:
        print(f"\n=== {t['label']} ===")
        out = client.chat(
            model=model,
            messages=t["messages"],
            max_output_tokens=t["max_output_tokens"],  # sent as max_completion_tokens for gpt-5
            temperature=None,  # omit for gpt-5
            response_format=None,
        )
        print("Raw:", out)
        # Try JSON parse if looks like JSON
        if out.strip().startswith("{"):
            try:
                import json
                print("JSON OK keys:", list(json.loads(out).keys()))
            except Exception as e:
                print("JSON parse error:", e)