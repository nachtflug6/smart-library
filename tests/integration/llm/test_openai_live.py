import os
import json
import logging
import pytest

from smart_library.llm.openai_client import OpenAIClient

RUN_LIVE = os.getenv("RUN_OPENAI_LIVE") == "1"
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_TEST_MODEL", "gpt-4o-mini")

logger = logging.getLogger(__name__)


def _valid_api_key(k: str | None) -> bool:
    return bool(k) and k.startswith("sk-") and len(k) > 20


# Skip unless explicitly opted-in with a valid key
pytestmark = pytest.mark.skipif(
    not (RUN_LIVE and _valid_api_key(API_KEY)),
    reason="Set RUN_OPENAI_LIVE=1 and a valid OPENAI_API_KEY (starts with 'sk-') to run live OpenAI tests.",
)


def _ensure_logger():
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[OPENAI LIVE] %(levelname)s %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)


@pytest.fixture(scope="module", autouse=True)
def _setup_logging():
    _ensure_logger()
    yield


@pytest.fixture(scope="module")
def client():
    # Extra guard in case mark didn’t apply
    if not _valid_api_key(API_KEY):
        pytest.skip("Invalid or missing OPENAI_API_KEY; skipping live OpenAI tests.")
    return OpenAIClient(api_key=API_KEY, default_model=MODEL)


def chat_and_log(client: OpenAIClient, *, model: str, messages, **kwargs) -> str:
    # Never log secrets; only log model, messages, and safe kwargs
    safe_kwargs = {k: v for k, v in kwargs.items() if k.lower() != "api_key"}
    logger.info("Request model=%s kwargs=%s", model, safe_kwargs)
    logger.info("Messages=%s", json.dumps(messages, ensure_ascii=False))
    out = client.chat(model=model, messages=messages, **kwargs)
    preview = out.strip().replace("\n", " ")
    if len(preview) > 300:
        preview = preview[:300] + "…"
    logger.info("Response len=%d preview=%s", len(out), preview)
    return out


def test_simple_completion(client):
    out = chat_and_log(
        client,
        model=MODEL,
        messages=[{"role": "user", "content": "Say 'hello' in one short sentence."}],
        max_output_tokens=32,
        temperature=0.2,
    )
    assert isinstance(out, str)
    assert len(out.strip()) > 0
    assert "hello" in out.lower()


def test_json_response_format(client):
    out = chat_and_log(
        client,
        model=MODEL,
        messages=[
            {"role": "system", "content": "Return only valid JSON. No extra text."},
            {"role": "user", "content": "Return an object with keys: ok=true, model, ts (unix)."},
        ],
        max_output_tokens=128,
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    data = json.loads(out)
    logger.info("Parsed JSON=%s", json.dumps(data, ensure_ascii=False))
    assert isinstance(data, dict)
    assert "ok" in data and data["ok"] in (True, "true", 1)
    assert "model" in data
    assert "ts" in data


def test_token_limit_smoke(client):
    out = chat_and_log(
        client,
        model=MODEL,
        messages=[{"role": "user", "content": "Write a long paragraph of at least 300 words about testing."}],
        max_output_tokens=64,
        temperature=0.7,
    )
    assert isinstance(out, str)
    assert 1 <= len(out.strip()) <= 2000