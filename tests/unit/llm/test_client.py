"""Unit tests for LLMClient base class."""

import pytest
from smart_library.llm.client import LLMClient


class FakeLLMClient(LLMClient):
    """Test implementation of LLMClient."""
    
    def __init__(self, api_key: str, default_model: str, response: str = "test_response"):
        super().__init__(api_key=api_key, default_model=default_model)
        self.response = response
        self.last_call = None
    
    def _call_api(
        self,
        model: str,
        messages,
        temperature: float,
        max_output_tokens: int,
        **kwargs,
    ) -> str:
        """Record call parameters and return canned response."""
        self.last_call = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
            "kwargs": kwargs,
        }
        return self.response


def test_chat_uses_default_model():
    """Test that chat() uses default_model when model not specified."""
    client = FakeLLMClient(api_key="test_key", default_model="model-default")
    messages = [{"role": "user", "content": "hello"}]
    
    result = client.chat(messages)
    
    assert result == "test_response"
    assert client.last_call["model"] == "model-default"
    assert client.last_call["messages"] is messages


def test_chat_uses_default_parameters():
    """Test that chat() uses default temperature and max_output_tokens."""
    client = FakeLLMClient(api_key="test_key", default_model="model-x")
    messages = [{"role": "user", "content": "test"}]
    
    result = client.chat(messages)
    
    assert client.last_call["temperature"] == 0.7
    assert client.last_call["max_output_tokens"] == 1024


def test_chat_overrides_model():
    """Test that chat() can override default_model."""
    client = FakeLLMClient(api_key="test_key", default_model="model-default")
    messages = [{"role": "user", "content": "test"}]
    
    result = client.chat(messages, model="model-override")
    
    assert client.last_call["model"] == "model-override"


def test_chat_overrides_temperature():
    """Test that chat() can override temperature."""
    client = FakeLLMClient(api_key="test_key", default_model="model-x")
    messages = [{"role": "user", "content": "test"}]
    
    result = client.chat(messages, temperature=1.5)
    
    assert client.last_call["temperature"] == 1.5


def test_chat_overrides_max_output_tokens():
    """Test that chat() can override max_output_tokens."""
    client = FakeLLMClient(api_key="test_key", default_model="model-x")
    messages = [{"role": "user", "content": "test"}]
    
    result = client.chat(messages, max_output_tokens=2048)
    
    assert client.last_call["max_output_tokens"] == 2048


def test_chat_forwards_arbitrary_kwargs():
    """Test that chat() forwards additional kwargs to _call_api."""
    client = FakeLLMClient(api_key="test_key", default_model="model-x")
    messages = [{"role": "user", "content": "test"}]
    
    result = client.chat(
        messages,
        top_p=0.9,
        user="user123",
        response_format="json",
    )
    
    assert client.last_call["kwargs"]["top_p"] == 0.9
    assert client.last_call["kwargs"]["user"] == "user123"
    assert client.last_call["kwargs"]["response_format"] == "json"


def test_chat_passes_messages_unchanged():
    """Test that chat() doesn't modify the messages list."""
    client = FakeLLMClient(api_key="test_key", default_model="model-x")
    messages = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello"},
    ]
    
    result = client.chat(messages)
    
    # Should pass the exact same object
    assert client.last_call["messages"] is messages


def test_initialization_stores_api_key():
    """Test that __init__ stores api_key."""
    client = FakeLLMClient(api_key="secret_key", default_model="model-x")
    
    assert client.api_key == "secret_key"


def test_initialization_stores_default_model():
    """Test that __init__ stores default_model."""
    client = FakeLLMClient(api_key="key", default_model="my-model")
    
    assert client.default_model == "my-model"


def test_chat_returns_response_from_call_api():
    """Test that chat() returns whatever _call_api returns."""
    client = FakeLLMClient(
        api_key="key",
        default_model="model-x",
        response="custom_response_text"
    )
    messages = [{"role": "user", "content": "test"}]
    
    result = client.chat(messages)
    
    assert result == "custom_response_text"