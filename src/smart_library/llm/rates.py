from __future__ import annotations
from typing import List, Dict, Any, Tuple, Optional
import threading
import time

# Hard-coded per-model limits based on OpenAI quotas.
# TPD (tokens per day) not enforced in this limiter (minute-window only).
MODEL_LIMITS: dict[str, dict[str, int]] = {
    # GPT-5 family
    "gpt-5": {"rpm": 500, "tpm": 500_000, "tpd": 1_500_000},
    "gpt-5-mini": {"rpm": 500, "tpm": 500_000, "tpd": 5_000_000},
    "gpt-5-nano": {"rpm": 500, "tpm": 200_000, "tpd": 2_000_000},

    # GPT-4.1 family
    "gpt-4.1": {"rpm": 500, "tpm": 30_000, "tpd": 900_000},
    "gpt-4.1-mini": {"rpm": 500, "tpm": 200_000, "tpd": 2_000_000},
    "gpt-4.1-nano": {"rpm": 500, "tpm": 200_000, "tpd": 2_000_000},

    # o-series
    "o3": {"rpm": 500, "tpm": 30_000, "tpd": 90_000},
    "o4-mini": {"rpm": 500, "tpm": 200_000, "tpd": 2_000_000},

    # GPT-4o family
    "gpt-4o": {"rpm": 500, "tpm": 30_000, "tpd": 90_000},
}

def norm_model(model: str) -> str:
    return (model or "").strip().lower()

def estimate_message_tokens(messages: List[Dict[str, Any]], model: str) -> int:
    """
    Approximate token count for chat messages.
    Uses tiktoken when available; else falls back to a /4 heuristic.
    """
    try:
        import tiktoken
        try:
            enc = tiktoken.encoding_for_model(model)
        except KeyError:
            enc = tiktoken.get_encoding("cl100k_base")
    except Exception:
        # Rough fallback: chars/4 + small overhead
        return sum(
            (len(m.get("role", "")) + len(m.get("content", "") or "")) // 4 + 4
            for m in messages
        ) + 2

    tokens = 0
    for m in messages:
        role = m.get("role", "")
        content = m.get("content", "") or ""
        tokens += len(enc.encode(role)) + len(enc.encode(content)) + 4  # per-message overhead
    tokens += 2  # assistant priming
    return tokens

def get_model_limits(
    model: Optional[str],
    *,
    default_rpm: int | None = None,
    default_tpm: int | None = None,
) -> Tuple[int | None, int | None]:
    """
    Look up per-model limits from MODEL_LIMITS, falling back to provided defaults.
    """
    if model:
        key = norm_model(model)
        cfg = MODEL_LIMITS.get(key)
        if cfg:
            return cfg.get("rpm"), cfg.get("tpm")

    return default_rpm, default_tpm

class MinuteRateLimiter:
    """
    Thread-safe minute window limiter for tokens & requests. Blocks until within limits.
    """
    def __init__(self, tpm_limit: int | None, rpm_limit: int | None):
        self.tpm_limit = tpm_limit
        self.rpm_limit = rpm_limit
        self._lock = threading.Lock()
        self._window_start = time.time()
        self._used_tokens = 0
        self._used_requests = 0

    def _reset_if_needed(self):
        """Reset counters if minute window has passed."""
        if time.time() - self._window_start >= 60:
            self._window_start = time.time()
            self._used_tokens = 0
            self._used_requests = 0

    def acquire(self, tokens_needed: int):
        """Block until request can proceed within rate limits."""
        while True:
            with self._lock:
                self._reset_if_needed()
                new_tokens = self._used_tokens + tokens_needed
                new_requests = self._used_requests + 1
                over_tpm = self.tpm_limit is not None and new_tokens > self.tpm_limit
                over_rpm = self.rpm_limit is not None and new_requests > self.rpm_limit
                if not over_tpm and not over_rpm:
                    self._used_tokens = new_tokens
                    self._used_requests = new_requests
                    return
                wait = max(60 - (time.time() - self._window_start), 0.05)
            time.sleep(min(wait, 5.0))

    def add_output_tokens(self, tokens: int):
        """Add output tokens to the current window count."""
        with self._lock:
            self._reset_if_needed()
            self._used_tokens += tokens


__all__ = [
    "MODEL_LIMITS",
    "norm_model",
    "get_model_limits",
    "estimate_message_tokens",
    "MinuteRateLimiter",
]