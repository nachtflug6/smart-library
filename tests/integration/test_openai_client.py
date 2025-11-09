"""
Integration tests for OpenAIClient.
Requires OPENAI_API_KEY in environment.
Makes real API calls - not unit tests.
"""
import os
import json
import pytest

from smart_library.llm.openai_client import OpenAIClient


@pytest.fixture
def api_key():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        pytest.skip("OPENAI_API_KEY not set")
    return key


@pytest.fixture
def client(api_key):
    return OpenAIClient(api_key=api_key, default_model="gpt-4o")


def test_plain_text_response(client):
    sys_msg = {"role": "system", "content": "You are concise. Reply with a single word."}
    user_msg = {"role": "user", "content": "Say hello in Spanish."}
    
    for model in ["gpt-4o", "gpt-4o-mini"]:
        out = client.chat(model=model, messages=[sys_msg, user_msg])
        assert out
        print(f"{model}: {out}")


def test_json_response_format(client):
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
    
    for model in ["gpt-4o", "gpt-4o-mini"]:
        out = client.chat(model=model, messages=[json_sys, json_user], response_format=response_format)
        obj = json.loads(out)
        assert all(k in obj for k in ("title", "authors", "year"))
        print(f"{model}: {obj}")


def test_concurrent_dispatch(client):
    echo_sys = {"role": "system", "content": "Echo the user message exactly."}
    prompts = [
        [echo_sys, {"role": "user", "content": "A"}],
        [echo_sys, {"role": "user", "content": "B"}],
        [echo_sys, {"role": "user", "content": "C"}],
    ]
    
    outs = client.chat_concurrent(model="gpt-4o", list_of_messages=prompts, max_workers=3)
    assert len(outs) == 3
    print(f"Concurrent results: {outs}")


def test_rate_limit_info(client):
    for model in ["gpt-4o", "gpt-4o-mini"]:
        limits = client.model_limits(model=model)
        assert "rpm" in limits
        assert "tpm" in limits
        print(f"{model}: RPM={limits['rpm']}, TPM={limits['tpm']}")