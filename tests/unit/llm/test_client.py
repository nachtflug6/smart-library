"""Unit tests for smart_library.llm.client module (BaseLLMClient)."""

import json
import time
from typing import List, Dict, Any

import pytest

from smart_library.llm.client import BaseLLMClient


class FakeClient(BaseLLMClient):
    """Fake client for testing base functionality."""
    
    def __init__(self, delay_factor=0.001):
        super().__init__(default_model="gpt-5-mini")
        self.delay_factor = delay_factor
        self.call_log = []

    def _call_api(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        *,
        max_output_tokens: int | None = None,
        temperature: float = 0.0,
        response_format: dict | None = None,
    ) -> str:
        """Mock API call that logs and returns structured response."""
        self.call_log.append({
            "model": model,
            "messages": messages,
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
            "response_format": response_format,
        })
        
        last = next((m for m in reversed(messages) if m["role"] == "user"), {"content": ""})
        # Small deterministic delay based on content length to scramble completion order in threads
        time.sleep(self.delay_factor * (len(last["content"]) % 3))
        
        return json.dumps({
            "ok": True,
            "echo": last["content"],
            "model": model,
        })


def test_chat_basic():
    """Test basic chat call."""
    print("\n[chat_basic] Testing basic chat functionality")
    
    client = FakeClient()
    messages = [{"role": "user", "content": "Hello"}]
    
    print(f"[chat_basic] Input messages: {messages}")
    
    out = client.chat(
        model="gpt-5-mini",
        messages=messages,
    )
    
    print(f"[chat_basic] Output: {out}")
    
    obj = json.loads(out)
    assert obj["ok"] is True
    assert obj["echo"] == "Hello"
    assert obj["model"] == "gpt-5-mini"
    
    print("[chat_basic] Chat call successful ✓")


def test_chat_with_default_model():
    """Test chat using default model."""
    print("\n[chat_default_model] Testing with default model")
    
    client = FakeClient()
    messages = [{"role": "user", "content": "Test"}]
    
    print("[chat_default_model] Calling chat without explicit model")
    
    out = client.chat(messages=messages)
    
    obj = json.loads(out)
    print(f"[chat_default_model] Used model: {obj['model']}")
    
    assert obj["model"] == "gpt-5-mini"
    assert obj["echo"] == "Test"
    
    print("[chat_default_model] Default model used correctly ✓")


def test_chat_with_parameters():
    """Test chat with all parameters."""
    print("\n[chat_params] Testing chat with full parameters")
    
    client = FakeClient()
    messages = [{"role": "user", "content": "Parameterized"}]
    
    params = {
        "model": "gpt-4o",
        "messages": messages,
        "max_output_tokens": 100,
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }
    
    print(f"[chat_params] Input params: {json.dumps({k: v for k, v in params.items() if k != 'messages'}, indent=2)}")
    
    out = client.chat(**params)
    
    print(f"[chat_params] Output: {out}")
    
    # Check call was logged correctly
    assert len(client.call_log) == 1
    call = client.call_log[0]
    
    print(f"[chat_params] Logged call params: {list(call.keys())}")
    
    assert call["model"] == "gpt-4o"
    assert call["max_output_tokens"] == 100
    assert call["temperature"] == 0.7
    assert call["response_format"] == {"type": "json_object"}
    
    print("[chat_params] Parameters passed correctly ✓")


def test_chat_concurrent_order_and_count():
    """Test concurrent chat with order preservation."""
    print("\n[concurrent] Testing concurrent chat with order preservation")
    
    client = FakeClient()
    list_of_messages = [
        [{"role": "user", "content": f"msg-{i}"}] for i in range(10)
    ]
    
    print(f"[concurrent] Input: {len(list_of_messages)} message sets")
    for i, msgs in enumerate(list_of_messages[:3]):
        print(f"[concurrent]   [{i}]: {msgs}")
    print(f"[concurrent]   ... ({len(list_of_messages) - 3} more)")
    
    outs = client.chat_concurrent(
        model="gpt-5-mini",
        list_of_messages=list_of_messages,
        max_workers=4,
    )
    
    print(f"[concurrent] Output: {len(outs)} responses")
    assert len(outs) == len(list_of_messages)
    
    # Validate format and order
    for i, out in enumerate(outs):
        obj = json.loads(out)
        print(f"[concurrent]   [{i}]: echo='{obj['echo']}'")
        assert obj["ok"] is True
        assert obj["echo"] == f"msg-{i}"
    
    print("[concurrent] Order preserved ✓")


def test_chat_concurrent_with_single_worker():
    """Test concurrent chat with single worker (sequential)."""
    print("\n[concurrent_single] Testing concurrent with max_workers=1")
    
    client = FakeClient()
    list_of_messages = [
        [{"role": "user", "content": f"seq-{i}"}] for i in range(5)
    ]
    
    print(f"[concurrent_single] Input: {len(list_of_messages)} messages")
    
    outs = client.chat_concurrent(
        model="gpt-5-mini",
        list_of_messages=list_of_messages,
        max_workers=1,
    )
    
    print(f"[concurrent_single] Output: {len(outs)} responses")
    
    for i, out in enumerate(outs):
        obj = json.loads(out)
        assert obj["echo"] == f"seq-{i}"
    
    print("[concurrent_single] Sequential execution correct ✓")


def test_chat_concurrent_empty_list():
    """Test concurrent chat with empty input."""
    print("\n[concurrent_empty] Testing with empty message list")
    
    client = FakeClient()
    
    outs = client.chat_concurrent(
        model="gpt-5-mini",
        list_of_messages=[],
        max_workers=4,
    )
    
    print(f"[concurrent_empty] Output: {outs}")
    assert outs == []
    
    print("[concurrent_empty] Empty input handled correctly ✓")


def test_model_limits():
    """Test model_limits method."""
    print("\n[model_limits] Testing model_limits query")
    
    client = FakeClient()
    
    limits = client.model_limits("gpt-5-mini")
    
    print(f"[model_limits] Limits for gpt-5-mini: {limits}")
    
    assert isinstance(limits, dict)
    assert "rpm" in limits
    assert "tpm" in limits
    
    print("[model_limits] Limits retrieved ✓")


def test_chat_no_model_raises():
    """Test that chat without model raises when no default is set."""
    print("\n[chat_no_model] Testing error when no model specified")
    
    class ClientNoDefault(BaseLLMClient):
        def __init__(self):
            super().__init__(default_model=None)
        
        def _call_api(self, model, messages, **kwargs):
            return "test"
    
    client = ClientNoDefault()
    
    print("[chat_no_model] Calling chat without model parameter")
    
    with pytest.raises(ValueError, match="No model specified"):
        client.chat(messages=[{"role": "user", "content": "test"}])
    
    print("[chat_no_model] ValueError raised as expected ✓")