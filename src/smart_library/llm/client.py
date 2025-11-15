"""
Abstract base client with concurrency + optional rate-limiting.
Vendor-agnostic. Subclass must implement `_call_api`.

Rate limits and token estimation are injected via callables so vendor
clients can override without changing this base class.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Dict, Any, Callable, Tuple

from .rates import MinuteRateLimiter, estimate_message_tokens, get_model_limits


class BaseLLMClient(ABC):
    """
    Generic LLM client with chat + concurrent dispatch and optional rate limiting.
    Subclass must implement _call_api.
    """

    def __init__(
        self,
        *,
        default_model: Optional[str] = None,
        default_rpm: int | None = None,
        default_tpm: int | None = None,
        limits_provider: Callable[[Optional[str], int | None, int | None], Tuple[int | None, int | None]] = get_model_limits,
        token_estimator: Callable[[List[Dict[str, Any]], str], int] = estimate_message_tokens,
    ):
        self.default_model = default_model
        self.default_rpm = default_rpm
        self.default_tpm = default_tpm

        # Injected strategies (vendor-agnostic)
        self._limits_provider = limits_provider
        self._token_estimator = token_estimator

        # Per-model minute window limiters
        self._limiters: Dict[str, MinuteRateLimiter] = {}

    def _get_limiter(self, model: str) -> MinuteRateLimiter:
        key = (model or "").strip().lower()
        if key not in self._limiters:
            rpm, tpm = self._limits_provider(
                key, default_rpm=self.default_rpm, default_tpm=self.default_tpm
            )
            self._limiters[key] = MinuteRateLimiter(tpm_limit=tpm, rpm_limit=rpm)
        return self._limiters[key]

    @abstractmethod
    def _call_api(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        *,
        max_output_tokens: int | None = None,
        temperature: float = 0.0,
        response_format: Optional[dict] = None,
    ) -> str:
        """Backend-specific API call. Return text response."""
        raise NotImplementedError

    def chat(
        self,
        model: Optional[str] = None,
        messages: List[Dict[str, Any]] = None,
        *,
        max_output_tokens: int | None = None,
        temperature: float = 0.0,
        response_format: Optional[dict] = None,
        apply_rate_limit: bool = True,
    ) -> str:
        """Generic chat call with optional rate limiting."""
        if messages is None:
            messages = []
        if model is None:
            if not self.default_model:
                raise ValueError("No model specified and no default_model set.")
            model = self.default_model

        limiter = self._get_limiter(model)

        if apply_rate_limit:
            try:
                input_tokens = self._token_estimator(messages, model)
            except Exception:
                input_tokens = 0
            limiter.acquire(input_tokens)

        content = self._call_api(
            model=model,
            messages=messages,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            response_format=response_format,
        )

        if apply_rate_limit and content:
            try:
                output_tokens = self._token_estimator(
                    [{"role": "assistant", "content": content}], model
                )
            except Exception:
                output_tokens = 0
            limiter.add_output_tokens(output_tokens)

        return content

    def chat_concurrent(
        self,
        model: Optional[str],
        list_of_messages: List[List[Dict[str, Any]]],
        *,
        max_output_tokens: int | None = None,
        temperature: float = 0.0,
        max_workers: int = 6,
        response_format: Optional[dict] = None,
        apply_rate_limit: bool = True,
    ) -> List[str]:
        """Run many chat calls concurrently. Order preserved."""

        def _one(i: int, msgs: List[Dict[str, Any]]):
            try:
                txt = self.chat(
                    model=model,
                    messages=msgs,
                    max_output_tokens=max_output_tokens,
                    temperature=temperature,
                    response_format=response_format,
                    apply_rate_limit=apply_rate_limit,
                )
                return i, txt
            except Exception:
                # Swallow errors and return empty content to preserve order/count.
                return i, ""

        results: List[tuple[int, str]] = []
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            future_map = {
                pool.submit(_one, i, msgs): i for i, msgs in enumerate(list_of_messages)
            }
            for fut in as_completed(future_map):
                try:
                    results.append(fut.result())
                except Exception:
                    idx = future_map[fut]
                    results.append((idx, ""))

        results.sort(key=lambda x: x[0])
        return [r for _, r in results]

    def model_limits(self, model: Optional[str] = None) -> Dict[str, int | None]:
        """Return minute limits for a model using the injected provider."""
        m = model or self.default_model
        rpm, tpm = self._limits_provider(m, default_rpm=self.default_rpm, default_tpm=self.default_tpm)
        return {"rpm": rpm, "tpm": tpm}
