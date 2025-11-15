"""
OpenAI API client implementation.
"""
from __future__ import annotations
import os
import logging
import time
from typing import Any, Dict, List, Optional

import openai
from openai import OpenAI

from smart_library.llm.client import LLMClient

logger = logging.getLogger(__name__)


class OpenAIClient(LLMClient):
    """OpenAI API client."""

    def __init__(
        self,
        api_key: str,
        default_model: str = "gpt-4o-mini",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        validate_key: bool = True,
    ):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key
            default_model: Default model to use
            max_retries: Maximum number of retries on failure
            retry_delay: Base delay between retries (exponential backoff)
            validate_key: If True, validate API key on initialization

        Raises:
            openai.AuthenticationError: If validate_key=True and key is invalid
            openai.APIConnectionError: If validate_key=True and connection fails
        """
        super().__init__(api_key=api_key, default_model=default_model)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client = OpenAI(api_key=api_key)

        if validate_key:
            self._validate_api_key()

    def _validate_api_key(self):
        """
        Validate API key by making a minimal request to OpenAI.

        Raises:
            openai.AuthenticationError: If API key is invalid
            openai.APIConnectionError: If connection fails
        """
        logger.info("Validating OpenAI API key...")
        try:
            # Make a minimal request to validate the key
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
            )
            logger.info("OpenAI API key validated successfully (model=%s)", self.default_model)
        except openai.AuthenticationError as e:
            logger.error("Invalid OpenAI API key: %s", e)
            raise
        except openai.APIConnectionError as e:
            logger.error("Failed to connect to OpenAI API: %s", e)
            raise
        except Exception as e:
            logger.warning("Unexpected error during API key validation: %s", e)
            raise

    def _call_api(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_output_tokens: int,
        **kwargs,
    ) -> str:
        """Call OpenAI API with retry logic."""
        kwargs_api = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_output_tokens,
        }

        # Pass through additional kwargs (e.g., response_format)
        for key in ("response_format", "top_p", "frequency_penalty", "presence_penalty", "stop"):
            if key in kwargs:
                kwargs_api[key] = kwargs[key]

        def _attempt(k: dict) -> Any:
            return self.client.chat.completions.create(**k)

        for attempt in range(self.max_retries):
            try:
                resp = _attempt(kwargs_api)
                content = resp.choices[0].message.content or ""
                return content
            except openai.RateLimitError as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning("Rate limit hit, retrying in %.1fs... (attempt %d/%d)", delay, attempt + 1, self.max_retries)
                    time.sleep(delay)
                else:
                    logger.error("Rate limit exceeded after %d retries", self.max_retries)
                    raise
            except openai.APIError as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning("API error: %s, retrying in %.1fs... (attempt %d/%d)", e, delay, attempt + 1, self.max_retries)
                    time.sleep(delay)
                else:
                    logger.error("API error after %d retries: %s", self.max_retries, e)
                    raise
            except Exception as e:
                logger.error("Unexpected error calling OpenAI API: %s", e)
                raise

        raise RuntimeError("Should not reach here")


if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set. Skipping smoke test.")
        raise SystemExit(0)

    client = OpenAIClient(api_key=api_key, default_model="gpt-5-mini")

    model = "gpt-5-mini"
    tests = [
        {
            "label": "T1 simple word",
            "messages": [{"role": "user", "content": "Say Hello"}],
            "max_output_tokens": 64,
        },
        {
            "label": "T2 tiny JSON",
            "messages": [
                {"role": "system", "content": "Return only valid JSON. No extra text."},
                {"role": "user", "content": 'Give me {"ok": true} exactly.'},
            ],
            "max_output_tokens": 256,
        },
        {
            "label": "T3 metadata subset",
            "messages": [
                {"role": "system", "content": "Return JSON only."},
                {"role": "user", "content": "Title: Example Research\nAuthors: Alice Smith, Bob Lee\nReturn JSON with title, authors."},
            ],
            "max_output_tokens": 800,
        },
    ]

    for t in tests:
        print(f"\n=== {t['label']} ===")
        out = client.chat(
            model=model,
            messages=t["messages"],
            max_output_tokens=t["max_output_tokens"],  # sent as max_completion_tokens for gpt-5
            temperature=None,  # omit for gpt-5
            response_format=None,
        )
        print("Raw:", out)
        # Try JSON parse if looks like JSON
        if out.strip().startswith("{"):
            try:
                import json
                print("JSON OK keys:", list(json.loads(out).keys()))
            except Exception as e:
                print("JSON parse error:", e)