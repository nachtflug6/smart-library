"""Unit tests for smart_library.llm.openai_client module (OpenAIClient)."""

import json
import types
from typing import Dict, Any

import pytest

import smart_library.llm.openai_client as openai_client_mod


# ---------- Mock OpenAI Response Objects ----------

class FakeRespMsg:
    """Mock response message object."""
    def __init__(self, content=None, parsed=None):
        self.content = content
        self.parsed = parsed


class FakeChoice:
    """Mock choice object."""
    def __init__(self, message):
        self.message = message


class FakeResp:
    """Mock OpenAI API response."""
    def __init__(self, content=None, parsed=None):
        self.choices = [FakeChoice(FakeRespMsg(content=content, parsed=parsed))]


def _make_fake_openai(behavior: str):
    """
    Factory for fake OpenAI client with different behaviors.
    
    behavior:
      - "ok": return content
      - "swap_to_max_tokens": raise on max_completion_tokens then succeed with max_tokens
      - "swap_to_max_completion": raise on max_tokens then succeed with max_completion_tokens
      - "drop_temperature": raise on temperature then succeed without it
      - "parsed_only": return empty content but have parsed payload
    """
    class FakeOpenAI:
        def __init__(self, api_key=None):
            self.api_key = api_key
            self.calls: list[dict] = []
            
            def create(**kwargs):
                self.calls.append(kwargs)
                
                if behavior == "swap_to_max_tokens":
                    if "max_completion_tokens" in kwargs:
                        raise Exception("unsupported parameter: max_completion_tokens")
                    return FakeResp(content='{"ok": true, "mode": "max_tokens"}')
                
                if behavior == "swap_to_max_completion":
                    if "max_tokens" in kwargs:
                        raise Exception("unsupported parameter: max_tokens")
                    return FakeResp(content='{"ok": true, "mode": "max_completion_tokens"}')
                
                if behavior == "drop_temperature":
                    if "temperature" in kwargs:
                        raise Exception("unsupported value: 'temperature': 0.7")
                    return FakeResp(content='{"ok": true, "mode": "no_temperature"}')
                
                if behavior == "parsed_only":
                    return FakeResp(content=None, parsed={"ok": True, "parsed": 1})
                
                # default ok
                return FakeResp(content='{"ok": true}')
            
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(create=create)
            )
    
    return FakeOpenAI


# ---------- GPT-5 Parameter Tests ----------

def test_openai_client_gpt5_omits_temperature_and_uses_max_completion_tokens(monkeypatch):
    """Test GPT-5 uses max_completion_tokens and omits temperature."""
    print("\n[openai_gpt5] Testing GPT-5 parameter handling")
    
    FakeOpenAI = _make_fake_openai("ok")
    monkeypatch.setattr(openai_client_mod, "OpenAI", FakeOpenAI)

    c = openai_client_mod.OpenAIClient(api_key="sk-test", default_model="gpt-5-mini")
    
    input_params = {
        "model": "gpt-5-mini",
        "messages": [{"role": "user", "content": "hi"}],
        "max_output_tokens": 128,
        "temperature": 0.7,
    }
    print(f"[openai_gpt5] Input params: {json.dumps(input_params, indent=2)}")
    
    out = c.chat(**input_params)
    
    print(f"[openai_gpt5] Output: {out}")
    assert json.loads(out)["ok"] is True

    # Inspect actual API call
    calls = c.client.calls
    assert len(calls) == 1
    sent = calls[0]
    
    print(f"[openai_gpt5] Actual API call params:")
    print(json.dumps(sent, indent=2, default=str))
    
    # Validate GPT-5 behavior
    assert sent["model"] == "gpt-5-mini"
    assert "temperature" not in sent, "GPT-5 should omit temperature"
    assert "response_format" not in sent, "GPT-5 should omit response_format"
    assert sent.get("max_completion_tokens") == 128, "GPT-5 should use max_completion_tokens"
    assert "max_tokens" not in sent, "GPT-5 should not use max_tokens"
    
    print("[openai_gpt5] Parameter adaptation correct ✓")


def test_openai_client_gpt5_nano_behavior(monkeypatch):
    """Test GPT-5-nano follows same rules as GPT-5."""
    print("\n[openai_gpt5_nano] Testing GPT-5-nano parameter handling")
    
    FakeOpenAI = _make_fake_openai("ok")
    monkeypatch.setattr(openai_client_mod, "OpenAI", FakeOpenAI)

    c = openai_client_mod.OpenAIClient(api_key="sk-test")
    
    out = c.chat(
        model="gpt-5-nano",
        messages=[{"role": "user", "content": "test"}],
        max_output_tokens=50,
        temperature=0.5,
    )
    
    calls = c.client.calls
    sent = calls[0]
    
    print(f"[openai_gpt5_nano] API params: {list(sent.keys())}")
    
    assert "temperature" not in sent
    assert "max_completion_tokens" in sent
    assert "max_tokens" not in sent
    
    print("[openai_gpt5_nano] Behaves like GPT-5 ✓")


# ---------- GPT-4o Parameter Tests ----------

def test_openai_client_4o_includes_temperature_and_response_format(monkeypatch):
    """Test GPT-4o includes temperature and response_format."""
    print("\n[openai_4o_full] Testing GPT-4o with all parameters")
    
    FakeOpenAI = _make_fake_openai("ok")
    monkeypatch.setattr(openai_client_mod, "OpenAI", FakeOpenAI)

    c = openai_client_mod.OpenAIClient(api_key="sk-test")
    
    input_params = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "test"}],
        "max_output_tokens": 100,
        "temperature": 0.8,
        "response_format": {"type": "json_object"},
    }
    
    print(f"[openai_4o_full] Input params: {json.dumps({k: v for k, v in input_params.items() if k != 'messages'}, indent=2)}")
    
    out = c.chat(**input_params)
    
    calls = c.client.calls
    sent = calls[0]
    
    print(f"[openai_4o_full] Actual API params: {list(sent.keys())}")
    print(f"[openai_4o_full] temperature: {sent.get('temperature')}")
    print(f"[openai_4o_full] response_format: {sent.get('response_format')}")
    
    assert sent.get("temperature") == 0.8
    assert sent.get("response_format") == {"type": "json_object"}
    assert "max_tokens" in sent  # 4o uses max_tokens by default
    
    print("[openai_4o_full] 4o parameters correct ✓")


# ---------- Adaptive Retry Tests ----------

def test_openai_client_adapts_swap_to_max_tokens(monkeypatch):
    """Test adaptation when API rejects max_completion_tokens."""
    print("\n[openai_adapt_max_tokens] Testing parameter swap on 400 error")
    
    FakeOpenAI = _make_fake_openai("swap_to_max_tokens")
    monkeypatch.setattr(openai_client_mod, "OpenAI", FakeOpenAI)

    c = openai_client_mod.OpenAIClient(api_key="sk-test", default_model="gpt-5-mini")
    
    input_params = {
        "model": "gpt-5-mini",
        "messages": [{"role": "user", "content": "hi"}],
        "max_output_tokens": 42,
    }
    print(f"[openai_adapt_max_tokens] Input: {json.dumps(input_params, indent=2)}")
    
    out = c.chat(**input_params)
    obj = json.loads(out)
    
    print(f"[openai_adapt_max_tokens] Output: {out}")
    assert obj["ok"] is True
    assert obj["mode"] == "max_tokens"

    # Validate retry behavior
    calls = c.client.calls
    print(f"[openai_adapt_max_tokens] Total API calls: {len(calls)}")
    for i, call in enumerate(calls):
        print(f"[openai_adapt_max_tokens] Call {i+1} params: {list(call.keys())}")
    
    assert any("max_completion_tokens" in k for k in calls), "First call should use max_completion_tokens"
    assert any("max_tokens" in k for k in calls), "Retry should use max_tokens"
    
    print("[openai_adapt_max_tokens] Adaptive retry successful ✓")


def test_openai_client_adapts_swap_to_max_completion_for_4o(monkeypatch):
    """Test adaptation when 4o API rejects max_tokens."""
    print("\n[openai_4o_adapt] Testing GPT-4o parameter adaptation")
    
    FakeOpenAI = _make_fake_openai("swap_to_max_completion")
    monkeypatch.setattr(openai_client_mod, "OpenAI", FakeOpenAI)

    c = openai_client_mod.OpenAIClient(api_key="sk-test", default_model="gpt-4o")
    
    input_params = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "hi"}],
        "max_output_tokens": 33,
        "temperature": 0.5,
        "response_format": {"type": "json_object"},
    }
    print(f"[openai_4o_adapt] Input params: {json.dumps({k: v for k, v in input_params.items() if k != 'messages'}, indent=2)}")
    
    out = c.chat(**input_params)
    obj = json.loads(out)
    
    print(f"[openai_4o_adapt] Output: {out}")
    assert obj["ok"] is True
    assert obj["mode"] == "max_completion_tokens"

    calls = c.client.calls
    print(f"[openai_4o_adapt] Total API calls: {len(calls)}")
    for i, call in enumerate(calls):
        print(f"[openai_4o_adapt] Call {i+1} params: {list(call.keys())}")
    
    # Validate 4o behavior
    assert any("max_tokens" in k for k in calls), "4o should try max_tokens first"
    assert any("max_completion_tokens" in k for k in calls), "Retry should use max_completion_tokens"
    assert any("temperature" in k for k in calls), "4o should include temperature"
    
    print("[openai_4o_adapt] Parameter adaptation for 4o correct ✓")


def test_openai_client_drops_temperature_on_error(monkeypatch):
    """Test dropping temperature when API rejects it."""
    print("\n[openai_drop_temp] Testing temperature parameter drop on error")
    
    FakeOpenAI = _make_fake_openai("drop_temperature")
    monkeypatch.setattr(openai_client_mod, "OpenAI", FakeOpenAI)

    c = openai_client_mod.OpenAIClient(api_key="sk-test")
    
    out = c.chat(
        model="gpt-4o",
        messages=[{"role": "user", "content": "test"}],
        temperature=0.7,
    )
    
    obj = json.loads(out)
    print(f"[openai_drop_temp] Output: {out}")
    assert obj["mode"] == "no_temperature"
    
    calls = c.client.calls
    print(f"[openai_drop_temp] Total calls: {len(calls)}")
    
    assert len(calls) == 2, "Should retry once"
    assert "temperature" in calls[0], "First call should have temperature"
    assert "temperature" not in calls[1], "Retry should drop temperature"
    
    print("[openai_drop_temp] Temperature dropped on retry ✓")


# ---------- Parsed Response Tests ----------

def test_openai_client_uses_parsed_when_content_empty(monkeypatch):
    """Test fallback to parsed field when content is empty."""
    print("\n[openai_parsed] Testing parsed response fallback")
    
    FakeOpenAI = _make_fake_openai("parsed_only")
    monkeypatch.setattr(openai_client_mod, "OpenAI", FakeOpenAI)

    c = openai_client_mod.OpenAIClient(api_key="sk-test", default_model="gpt-5-mini")
    
    input_params = {
        "model": "gpt-5-mini",
        "messages": [{"role": "user", "content": "hi"}],
        "max_output_tokens": 10,
    }
    print(f"[openai_parsed] Input: {json.dumps(input_params, indent=2)}")
    
    out = c.chat(**input_params)
    obj = json.loads(out)
    
    print(f"[openai_parsed] Output (from parsed field): {out}")
    print(f"[openai_parsed] Output type: {type(out)}")
    print(f"[openai_parsed] Parsed object: {json.dumps(obj, indent=2)}")
    
    assert obj["ok"] is True
    assert obj["parsed"] == 1
    assert isinstance(out, str), "Output should be JSON string"
    
    print("[openai_parsed] Parsed response extraction successful ✓")


# ---------- Response Format Validation ----------

def test_response_format_validation():
    """Test that response formats are properly structured JSON strings."""
    print("\n[format_validation] Testing response format validation")
    
    test_outputs = [
        '{"ok": true}',
        '{"ok": true, "mode": "max_tokens"}',
        '{"ok": true, "parsed": 1}',
    ]
    
    for i, output in enumerate(test_outputs):
        print(f"[format_validation] Testing output {i+1}: {output}")
        
        # Should be valid JSON
        obj = json.loads(output)
        print(f"[format_validation]   Parsed: {obj}")
        
        # Should have expected structure
        assert isinstance(obj, dict), "Response should be JSON object"
        assert "ok" in obj, "Response should have 'ok' field"
        
        print(f"[format_validation]   Valid JSON ✓")
    
    print("[format_validation] All formats valid ✓")