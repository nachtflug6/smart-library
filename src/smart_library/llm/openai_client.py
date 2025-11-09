"""
OpenAI-specific implementation of BaseLLMClient.
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from openai import OpenAI

from smart_library.llm.client import BaseLLMClient
from smart_library.llm.rates import get_model_limits, estimate_message_tokens


class OpenAIClient(BaseLLMClient):
    """
    OpenAI backend with built-in rate limiting.
    Responsibilities:
      - Hold OpenAI client
      - Implement _call_api (single chat completion)
      - Inject OpenAI-specific rate limits and token estimation
    All concurrency + rate limiting logic lives in BaseLLMClient.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        default_model: Optional[str] = None,
        default_rpm: int | None = None,
        default_tpm: int | None = None,
    ):
        # Inject OpenAI-specific limits provider and token estimator
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
        temperature: float = 0.0,
        response_format: Optional[dict] = None,
    ) -> str:
        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_output_tokens is not None:
            kwargs["max_tokens"] = max_output_tokens
        if response_format is not None:
            kwargs["response_format"] = response_format

        resp = self.client.chat.completions.create(**kwargs)
        return (resp.choices[0].message.content or "").strip()


if __name__ == "__main__":
    """
    Lightweight integration checks for OpenAIClient.
    Requires OPENAI_API_KEY in the environment.
    These are not unit tests; they make real API calls.
    """
    import os
    import json

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set. Skipping OpenAIClient smoke tests.")
        raise SystemExit(0)

    client = OpenAIClient(api_key=api_key, default_model="gpt-4o")

    models = [
        "gpt-4o",        # widely available
        "gpt-4o-mini",   # lightweight variant
    ]

    print("\n=== 1) Plain text response ===")
    sys_msg = {"role": "system", "content": "You are concise. Reply with a single word."}
    user_msg = {"role": "user", "content": "Say hello in Spanish."}
    for m in models:
        try:
            out = client.chat(model=m, messages=[sys_msg, user_msg])
            print(f"{m}: {out}")
        except Exception as e:
            print(f"{m}: ERROR -> {e}")

    print("\n=== 2) JSON response_format ===")
    json_sys = {
        "role": "system",
        "content": "Return only a JSON object with keys: title, authors, year. "
                   "Use null for missing values. No extra text."
    }
    json_user = {
        "role": "user",
        "content": "Paper: 'Attention Is All You Need' by Vaswani et al., 2017."
    }
    response_format = {"type": "json_object"}
    for m in models:
        try:
            out = client.chat(model=m, messages=[json_sys, json_user], response_format=response_format)
            obj = json.loads(out)
            ok_keys = all(k in obj for k in ("title", "authors", "year"))
            print(f"{m}: JSON OK={ok_keys} -> {out}")
        except Exception as e:
            print(f"{m}: JSON ERROR -> {e}")

    print("\n=== 3) Concurrent dispatch ===")
    echo_sys = {"role": "system", "content": "Echo the user message exactly."}
    prompts = [
        [echo_sys, {"role": "user", "content": "A"}],
        [echo_sys, {"role": "user", "content": "B"}],
        [echo_sys, {"role": "user", "content": "C"}],
    ]
    try:
        outs = client.chat_concurrent(model=models[0], list_of_messages=prompts, max_workers=3)
        print(f"Concurrent ({models[0]}): {outs}")
    except Exception as e:
        print(f"Concurrent ERROR: {e}")

    print("\n=== 4) Rate limit info ===")
    for m in models:
        limits = client.model_limits(model=m)
        print(f"{m}: RPM={limits['rpm']}, TPM={limits['tpm']}")