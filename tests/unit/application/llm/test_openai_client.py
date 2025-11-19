import importlib
import sys
from types import SimpleNamespace, ModuleType

import pytest


def _setup_fake_openai_and_reload(monkeypatch):
    """
    Install a fake 'openai' module into sys.modules and reload the client module
    so it uses our fakes. Returns (openai_client_module, behavior, make_resp, fake_openai_module).
    """
    behavior = SimpleNamespace(script=[], calls=[])

    fake_openai = ModuleType("openai")

    class RateLimitError(Exception):
        pass

    class APIError(Exception):
        pass

    def create_impl(**kwargs):
        # Record every API call
        behavior.calls.append(kwargs)
        # Drive behavior from the script queue
        if behavior.script:
            action = behavior.script.pop(0)
            if action[0] == "raise":
                kind = action[1]
                if kind == "rate_limit":
                    raise RateLimitError("rate limit")
                if kind == "api_error":
                    raise APIError("api error")
            if action[0] == "return":
                return action[1]
        # Default empty response
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=""))]
        )

    class FakeOpenAI:
        def __init__(self, api_key: str):
            # Emulate client.chat.completions.create(...)
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=create_impl)
            )

    fake_openai.RateLimitError = RateLimitError
    fake_openai.APIError = APIError
    fake_openai.OpenAI = FakeOpenAI

    monkeypatch.setitem(sys.modules, "openai", fake_openai)

    import smart_library.application.llm.openai_client as openai_client

    # Ensure the module sees our fake 'openai' and 'OpenAI'
    openai_client = importlib.reload(openai_client)

    def make_resp(content=None, parsed=None):
        msg = SimpleNamespace(content=content, parsed=parsed)
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)])

    return openai_client, behavior, make_resp, fake_openai


def test_call_api_maps_parameters_and_pass_through_kwargs(monkeypatch):
    openai_client, behavior, make_resp, _ = _setup_fake_openai_and_reload(monkeypatch)

    # Prepare fake response
    behavior.script.append(("return", make_resp(content="ok")))

    client = openai_client.OpenAIClient(api_key="key", default_model="model-a", validate_key=False)

    messages = [{"role": "user", "content": "Hello"}]
    _ = client.chat(
        messages,
        model="model-b",
        temperature=0.3,
        max_output_tokens=77,
        response_format="json_object",
        top_p=0.9,
        frequency_penalty=0.2,
        presence_penalty=0.4,
        stop=["\n\n"],
    )

    assert len(behavior.calls) == 1
    kwargs = behavior.calls[0]

    # Base mapping
    assert kwargs["model"] == "model-b"
    assert kwargs["messages"] is messages
    assert kwargs["temperature"] == 0.3
    assert kwargs["max_tokens"] == 77  # mapped from max_output_tokens

    # Pass-throughs
    assert kwargs["response_format"] == "json_object"
    assert kwargs["top_p"] == 0.9
    assert kwargs["frequency_penalty"] == 0.2
    assert kwargs["presence_penalty"] == 0.4
    assert kwargs["stop"] == ["\n\n"]


def test_returns_parsed_when_content_empty(monkeypatch):
    openai_client, behavior, make_resp, _ = _setup_fake_openai_and_reload(monkeypatch)

    # Simulate empty content but parsed payload
    parsed = {"a": 1, "b": "x"}
    behavior.script.append(("return", make_resp(content="", parsed=parsed)))

    client = openai_client.OpenAIClient(api_key="key", validate_key=False)
    messages = [{"role": "user", "content": "give json"}]

    result = client.chat(messages)

    # Expect JSON string (client json.dumps the parsed field)
    import json as _json

    assert result == _json.dumps(parsed, ensure_ascii=False)


def test_retries_on_rate_limit_then_succeeds(monkeypatch):
    openai_client, behavior, make_resp, fake_openai = _setup_fake_openai_and_reload(monkeypatch)

    # Avoid real sleeping during retries
    monkeypatch.setattr(openai_client.time, "sleep", lambda _: None)

    # Two rate limits, then success
    behavior.script.extend([
        ("raise", "rate_limit"),
        ("raise", "rate_limit"),
        ("return", make_resp(content="final")),
    ])

    client = openai_client.OpenAIClient(
        api_key="key",
        max_retries=3,
        retry_delay=0.01,
        validate_key=False,
    )

    messages = [{"role": "user", "content": "retry please"}]
    result = client.chat(messages)

    assert result == "final"
    assert len(behavior.calls) == 3  # two failures + one success


def test_raises_after_api_error_exhausted(monkeypatch):
    openai_client, behavior, _, fake_openai = _setup_fake_openai_and_reload(monkeypatch)

    # Avoid sleeping
    monkeypatch.setattr(openai_client.time, "sleep", lambda _: None)

    # Always API error
    behavior.script.extend([("raise", "api_error"), ("raise", "api_error")])

    client = openai_client.OpenAIClient(
        api_key="key", max_retries=2, retry_delay=0.01, validate_key=False
    )
    messages = [{"role": "user", "content": "boom"}]

    with pytest.raises(fake_openai.APIError):
        _ = client.chat(messages)


def test_validate_key_calls_api_on_init(monkeypatch):
    openai_client, behavior, make_resp, _ = _setup_fake_openai_and_reload(monkeypatch)

    # First call from validation, second from chat
    behavior.script.append(("return", make_resp(content="v-ok")))

    client = openai_client.OpenAIClient(api_key="key", default_model="gpt-4o-mini", validate_key=True)

    # One call should have happened during validation
    assert len(behavior.calls) == 1
    init_kwargs = behavior.calls[0]
    assert init_kwargs["model"] == "gpt-4o-mini"
    assert init_kwargs["messages"] == [{"role": "user", "content": "test"}]
    assert init_kwargs["max_tokens"] == 1

    # And chat still works
    behavior.script.append(("return", make_resp(content="chat-ok")))
    messages = [{"role": "user", "content": "go"}]
    out = client.chat(messages, temperature=0.5, max_output_tokens=5)

    assert out == "chat-ok"