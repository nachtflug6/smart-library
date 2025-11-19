"""Unit tests for smart_library.llm.rates module."""

import pytest

from smart_library.llm.rates import (
    estimate_message_tokens,
    get_model_limits,
    MinuteRateLimiter,
    MODEL_LIMITS,
)


def test_estimate_message_tokens_basic():
    """Test basic token estimation for chat messages."""
    msgs = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Say hello to the world."},
    ]
    print("\n[estimate_tokens] Input messages:")
    for m in msgs:
        print(f"  {m['role']}: {m['content']}")
    
    n = estimate_message_tokens(msgs, model="gpt-5-mini")
    
    print(f"[estimate_tokens] Estimated tokens: {n}")
    print(f"[estimate_tokens] Token type: {type(n)}")
    
    assert isinstance(n, int)
    assert n > 0


def test_estimate_message_tokens_empty():
    """Test token estimation with empty messages."""
    msgs = []
    print("\n[estimate_tokens_empty] Input: empty list")
    
    n = estimate_message_tokens(msgs, model="gpt-5-mini")
    
    print(f"[estimate_tokens_empty] Estimated tokens: {n}")
    assert isinstance(n, int)
    assert n >= 0


def test_estimate_message_tokens_long_content():
    """Test token estimation with longer content."""
    long_text = "This is a much longer message. " * 50
    msgs = [
        {"role": "user", "content": long_text},
    ]
    print(f"\n[estimate_tokens_long] Input content length: {len(long_text)} chars")
    
    n = estimate_message_tokens(msgs, model="gpt-5-mini")
    
    print(f"[estimate_tokens_long] Estimated tokens: {n}")
    assert isinstance(n, int)
    assert n > 100  # Should be substantial for long text


def test_get_model_limits_known_model():
    """Test model limits lookup for known model."""
    model = "gpt-5-mini"
    
    print(f"\n[model_limits_known] Input model: {model}")
    
    rpm, tpm = get_model_limits(model, default_rpm=123, default_tpm=456)
    
    print(f"[model_limits_known] Output RPM: {rpm}")
    print(f"[model_limits_known] Output TPM: {tpm}")
    
    # Should return actual limits from MODEL_LIMITS, not defaults
    expected_rpm = MODEL_LIMITS["gpt-5-mini"]["rpm"]
    expected_tpm = MODEL_LIMITS["gpt-5-mini"]["tpm"]
    
    print(f"[model_limits_known] Expected RPM: {expected_rpm}, TPM: {expected_tpm}")
    
    assert rpm == expected_rpm
    assert tpm == expected_tpm
    assert rpm == 500
    assert tpm == 500_000


def test_get_model_limits_unknown_model_uses_defaults():
    """Test model limits with unknown model falls back to defaults."""
    model = "unknown-model-xyz"
    default_rpm = 123
    default_tpm = 456
    
    print(f"\n[model_limits_unknown] Input model: {model}")
    print(f"[model_limits_unknown] Default RPM: {default_rpm}")
    print(f"[model_limits_unknown] Default TPM: {default_tpm}")
    
    rpm, tpm = get_model_limits(model, default_rpm=default_rpm, default_tpm=default_tpm)
    
    print(f"[model_limits_unknown] Output RPM: {rpm}")
    print(f"[model_limits_unknown] Output TPM: {tpm}")
    
    assert rpm == default_rpm
    assert tpm == default_tpm


def test_get_model_limits_none_defaults():
    """Test model limits with None defaults for unknown model."""
    print("\n[model_limits_none] Testing with None defaults")
    
    rpm, tpm = get_model_limits("unknown-model", default_rpm=None, default_tpm=None)
    
    print(f"[model_limits_none] RPM: {rpm}, TPM: {tpm}")
    assert rpm is None
    assert tpm is None


def test_get_model_limits_case_insensitive():
    """Test that model lookup is case-insensitive."""
    print("\n[model_limits_case] Testing case-insensitive lookup")
    
    models = ["gpt-5-mini", "GPT-5-MINI", "Gpt-5-Mini", "GPT-5-mini"]
    
    for model in models:
        print(f"[model_limits_case] Testing model: '{model}'")
        rpm, tpm = get_model_limits(model)
        
        print(f"[model_limits_case]   RPM: {rpm}, TPM: {tpm}")
        
        assert rpm == 500
        assert tpm == 500_000
    
    print("[model_limits_case] All case variations matched ✓")


def test_get_model_limits_all_known_models():
    """Test that all models in MODEL_LIMITS can be looked up."""
    print("\n[model_limits_all] Testing all known models")
    
    for model_key in MODEL_LIMITS.keys():
        print(f"[model_limits_all] Testing model: {model_key}")
        
        rpm, tpm = get_model_limits(model_key)
        
        expected_rpm = MODEL_LIMITS[model_key]["rpm"]
        expected_tpm = MODEL_LIMITS[model_key]["tpm"]
        
        print(f"[model_limits_all]   Got RPM: {rpm}, TPM: {tpm}")
        print(f"[model_limits_all]   Expected RPM: {expected_rpm}, TPM: {expected_tpm}")
        
        assert rpm == expected_rpm
        assert tpm == expected_tpm
    
    print(f"[model_limits_all] All {len(MODEL_LIMITS)} models validated ✓")


def test_get_model_limits_gpt4o():
    """Test specific GPT-4o limits."""
    print("\n[model_limits_4o] Testing GPT-4o limits")
    
    rpm, tpm = get_model_limits("gpt-4o")
    
    print(f"[model_limits_4o] RPM: {rpm}, TPM: {tpm}")
    
    assert rpm == 500
    assert tpm == 30_000


def test_minute_rate_limiter_basic_acquire():
    """Test basic rate limiter acquisition."""
    print("\n[rate_limiter_basic] Testing basic token acquisition")
    
    tpm_limit = 100
    rpm_limit = 10
    limiter = MinuteRateLimiter(tpm_limit=tpm_limit, rpm_limit=rpm_limit)
    
    print(f"[rate_limiter_basic] TPM limit: {tpm_limit}, RPM limit: {rpm_limit}")
    print(f"[rate_limiter_basic] Acquiring 10 tokens")
    
    limiter.acquire(10)
    
    print("[rate_limiter_basic] Acquisition successful ✓")


def test_minute_rate_limiter_resets_without_sleep(monkeypatch):
    """Test that rate limiter resets after minute window."""
    print("\n[rate_limiter] Testing minute window reset logic")
    
    # Control time to avoid real sleeps
    t = {"now": 0.0}

    def fake_time():
        return t["now"]

    def fake_sleep(_secs):
        t["now"] += 0.0

    monkeypatch.setattr("smart_library.llm.rates.time.time", fake_time)
    monkeypatch.setattr("smart_library.llm.rates.time.sleep", fake_sleep)

    tpm_limit = 10
    rpm_limit = 2
    print(f"[rate_limiter] TPM limit: {tpm_limit}")
    print(f"[rate_limiter] RPM limit: {rpm_limit}")
    
    limiter = MinuteRateLimiter(tpm_limit=tpm_limit, rpm_limit=rpm_limit)
    
    print(f"[rate_limiter] Time: {t['now']}s - Acquiring 5 tokens")
    limiter.acquire(5)
    print(f"[rate_limiter] Time: {t['now']}s - Acquiring 5 tokens")
    limiter.acquire(5)
    
    # Move time forward beyond 60s window to force reset
    t["now"] = 61.0
    print(f"[rate_limiter] Time: {t['now']}s (window reset) - Acquiring 5 tokens")
    limiter.acquire(5)  # Should pass due to reset
    
    print("[rate_limiter] All acquisitions passed ✓")


def test_minute_rate_limiter_add_output_tokens(monkeypatch):
    """Test adding output tokens to the rate limiter."""
    print("\n[rate_limiter_output] Testing output token tracking")
    
    t = {"now": 0.0}
    
    def fake_time():
        return t["now"]
    
    monkeypatch.setattr("smart_library.llm.rates.time.time", fake_time)
    
    limiter = MinuteRateLimiter(tpm_limit=100, rpm_limit=10)
    
    print("[rate_limiter_output] Acquiring 20 tokens")
    limiter.acquire(20)
    
    print("[rate_limiter_output] Adding 30 output tokens")
    limiter.add_output_tokens(30)
    
    print("[rate_limiter_output] Acquiring 40 more tokens")
    limiter.acquire(40)  # Total should be 90, under limit
    
    print("[rate_limiter_output] All operations successful ✓")


def test_minute_rate_limiter_none_limits():
    """Test rate limiter with no limits (None)."""
    print("\n[rate_limiter_none] Testing with no limits")
    
    limiter = MinuteRateLimiter(tpm_limit=None, rpm_limit=None)
    
    print("[rate_limiter_none] Acquiring large token count")
    limiter.acquire(1_000_000)
    
    print("[rate_limiter_none] Acquisition successful (no limits) ✓")