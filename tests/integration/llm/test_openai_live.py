import os
import json
import logging
import pytest

from smart_library.llm.openai_client import OpenAIClient, _mask_api_key
import openai

RUN_LIVE = os.getenv("RUN_OPENAI_LIVE") == "1"

# Sanitize API key (strip whitespace and accidental quotes)
API_KEY_RAW = os.getenv("OPENAI_API_KEY", "")
API_KEY = API_KEY_RAW.strip().strip('"').strip("'")

DEFAULT_MODEL = os.getenv("OPENAI_TEST_MODEL", "gpt-4o-mini")

logger = logging.getLogger(__name__)

# Models we want to exercise live
MODELS_TO_TEST = [
    "gpt-4o-mini",      # Latest mini model (recommended for testing)
    "gpt-4.1-mini",
    "gpt-4.1-nano",
]


def _valid_api_key(k: str | None) -> bool:
    if not k:
        return False
    s = k.strip().strip('"').strip("'")
    return s.startswith("sk-") and len(s) > 20


# Skip unless explicitly opted-in and API key is present
pytestmark = pytest.mark.skipif(
    not (RUN_LIVE and bool(API_KEY)),
    reason="Set RUN_OPENAI_LIVE=1 and OPENAI_API_KEY to run live OpenAI tests.",
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
    # Print diagnostic info
    logger.info("=" * 60)
    logger.info("DIAGNOSTIC: Checking OpenAI API key configuration")
    logger.info("RUN_OPENAI_LIVE=%s", os.getenv("RUN_OPENAI_LIVE"))
    logger.info("API_KEY masked=%s", _mask_api_key(API_KEY) if API_KEY else "NOT SET")
    logger.info("API_KEY raw len=%d sanitized len=%d", len(API_KEY_RAW), len(API_KEY))
    logger.info("API_KEY starts with 'sk-'=%s", API_KEY.startswith("sk-") if API_KEY else False)
    logger.info("DEFAULT_MODEL=%s", DEFAULT_MODEL)
    logger.info("MODELS_TO_TEST=%s", MODELS_TO_TEST)
    logger.info("=" * 60)
    yield


@pytest.fixture(scope="module")
def client():
    """Create client with default model for basic tests."""
    if not API_KEY:
        pytest.skip("Missing OPENAI_API_KEY; skipping live OpenAI tests.")
    return OpenAIClient(api_key=API_KEY, default_model=DEFAULT_MODEL, validate_key=True)


@pytest.fixture(scope="module", params=MODELS_TO_TEST)
def model_name(request):
    """Parametrize tests across multiple models."""
    return request.param


def chat_and_log(client: OpenAIClient, *, model: str, messages, **kwargs) -> str:
    safe_kwargs = {k: v for k, v in kwargs.items() if k.lower() != "api_key"}
    logger.info("Request model=%s kwargs=%s", model, safe_kwargs)
    logger.info("Messages=%s", json.dumps(messages, ensure_ascii=False))
    out = client.chat(model=model, messages=messages, **kwargs)
    preview = out.strip().replace("\n", " ")
    if len(preview) > 300:
        preview = preview[:300] + "…"
    logger.info("Response len=%d preview=%s", len(out), preview)
    return out


def test_api_key_validation_on_init():
    """Test that API key is validated during initialization."""
    client = OpenAIClient(api_key=API_KEY, default_model=DEFAULT_MODEL, validate_key=True)
    assert client is not None


def test_invalid_api_key_rejected():
    """Test that invalid API key is rejected during initialization."""
    with pytest.raises(openai.AuthenticationError):
        OpenAIClient(api_key="sk-invalid-key-test", default_model=DEFAULT_MODEL, validate_key=True)


def test_simple_completion_all_models(client, model_name):
    """Test simple completion across all models."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing model: %s", model_name)
    logger.info("=" * 60)

    out = chat_and_log(
        client,
        model=model_name,
        messages=[{"role": "user", "content": "Say 'hello' in one short sentence."}],
        max_output_tokens=1024,
        temperature=0.2,
    )
    text = out.strip()
    assert isinstance(out, str)
    assert len(text) > 0
    assert "hello" in text.lower()

    logger.info("✓ Model %s: passed simple completion", model_name)


def test_json_response_format_all_models(client, model_name):
    """Test JSON mode across all models.

    For GPT-5 models, JSON is enforced client-side (prompt + lenient parser),
    while 4o / 4.1 use server-side JSON mode via response_format.
    """
    logger.info("\n" + "=" * 60)
    logger.info("Testing JSON mode with model: %s", model_name)
    logger.info("=" * 60)

    out = chat_and_log(
        client,
        model=model_name,
        messages=[
            {"role": "system", "content": "Return only valid JSON. No extra text."},
            {"role": "user", "content": "Return an object with keys: ok=true, model, ts (unix)."},
        ],
        max_output_tokens=1024,
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    text = out.strip()
    assert text, f"Model {model_name} returned empty response in JSON mode"

    data = json.loads(text)
    logger.info("Parsed JSON=%s", json.dumps(data, ensure_ascii=False))
    assert isinstance(data, dict)
    assert "ok" in data and data["ok"] in (True, "true", 1)
    assert "model" in data
    assert "ts" in data

    logger.info("✓ Model %s: passed JSON response format", model_name)


def test_simple_completion_default_model(client):
    """Quick smoke test with just the default model."""
    out = chat_and_log(
        client,
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": "Say 'hello' in one short sentence."}],
        max_output_tokens=1024,
        temperature=0.2,
    )
    text = out.strip()
    assert isinstance(out, str)
    assert len(text) > 0
    assert "hello" in text.lower()


def test_json_response_format_default_model(client):
    """Quick JSON test with just the default model."""
    out = chat_and_log(
        client,
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": "Return only valid JSON. No extra text."},
            {"role": "user", "content": "Return an object with keys: ok=true, model, ts (unix)."},
        ],
        max_output_tokens=1024,
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    text = out.strip()
    assert text, "Default model returned empty response in JSON mode"

    data = json.loads(text)
    logger.info("Parsed JSON=%s", json.dumps(data, ensure_ascii=False))
    assert isinstance(data, dict)


def test_token_limit_smoke(client):
    """Test token limiting with default model.

    We only assert that the output is non-empty and not absurdly large,
    since exact character length vs. token limit is model-dependent.
    """
    out = chat_and_log(
        client,
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": "Write a long paragraph of at least 300 words about testing."}],
        max_output_tokens=1024,
        temperature=0.7,
    )
    text = out.strip()
    assert isinstance(out, str)
    assert len(text) > 0
    # Very loose upper bound just to catch runaway responses
    assert len(text) < 10_000


@pytest.mark.parametrize("model", ["gpt-4o-mini", "gpt-4o"])
def test_model_comparison(client, model):
    """Compare responses from different models for the same prompt."""
    logger.info("\n" + "=" * 60)
    logger.info("Model comparison test: %s", model)
    logger.info("=" * 60)

    prompt = "Explain what unit testing is in exactly 2 sentences."
    out = chat_and_log(
        client,
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_output_tokens=1024,
        temperature=0.5,
    )

    sentence_count = out.count(".") + out.count("!") + out.count("?")
    logger.info("Model %s generated %d sentences", model, sentence_count)

    assert isinstance(out, str)
    assert len(out.strip()) > 0
