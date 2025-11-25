"""
OpenAI API client implementation (clean, GPT-4-only).
"""
from __future__ import annotations
import logging
import time
import json
from typing import Any, Dict, List

import openai
from openai import OpenAI

logger = logging.getLogger(__name__)

class OpenAIClient:
    """OpenAI API client supporting GPT-4o / GPT-4.1 only."""

    def __init__(
        self,
        api_key: str,
        default_model: str = "gpt-4o-mini",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        validate_key: bool = True,
    ):
        self.api_key = api_key
        self.default_model = default_model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client = OpenAI(api_key=api_key)

        if validate_key:
            self._validate_api_key()

    # ---------------------------------------------------------------------
    #   API Key Validation
    # ---------------------------------------------------------------------
    def _validate_api_key(self):
        logger.info("Validating OpenAI API key...")
        try:
            self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
            )
            logger.info("OpenAI API key validated successfully (model=%s)", self.default_model)
        except Exception as e:
            logger.error("OpenAI key validation failed: %s", e)
            raise

    # ---------------------------------------------------------------------
    #   API Call
    # ---------------------------------------------------------------------
    def _call_api(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float | None,
        max_output_tokens: int | None,
        **kwargs,
    ) -> str:

        # Standard GPT-4o/4.1 parameters
        kwargs_api: Dict[str, Any] = {
            "model": model,
            "messages": messages,
        }

        # Temperature always allowed
        if temperature is not None:
            kwargs_api["temperature"] = temperature

        # Token limits (GPT-4 models use max_tokens)
        if max_output_tokens is not None:
            kwargs_api["max_tokens"] = max_output_tokens

        # Pass-through parameters
        for key in ("response_format", "top_p", "frequency_penalty", "presence_penalty", "stop"):
            if key in kwargs and kwargs[key] is not None:
                kwargs_api[key] = kwargs[key]

        # Retry loop ------------------------------------------------------
        for attempt in range(self.max_retries):
            try:
                resp = self.client.chat.completions.create(**kwargs_api)
                msg = resp.choices[0].message

                # Primary content
                content = (msg.content or "").strip()

                # Some GPT-4 models expose parsed JSON when response_format=json_object
                if not content:
                    parsed = getattr(msg, "parsed", None)
                    if parsed is not None:
                        try:
                            return json.dumps(parsed, ensure_ascii=False)
                        except Exception:
                            return str(parsed)

                return content

            except openai.RateLimitError:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(
                        "Rate limit hit, retrying in %.1fs... (attempt %d/%d)",
                        delay, attempt + 1, self.max_retries,
                    )
                    time.sleep(delay)
                    continue
                raise

            except openai.APIError as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(
                        "API error: %s, retrying in %.1fs... (attempt %d/%d)",
                        e, delay, attempt + 1, self.max_retries,
                    )
                    time.sleep(delay)
                    continue
                raise

            except Exception as e:
                logger.error("Unexpected error calling OpenAI API: %s", e)
                raise

        raise RuntimeError("Should not reach here")

    def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_output_tokens: int = 1024,
        **kwargs,
    ) -> str:
        """
        Send a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to self.default_model)
            temperature: Sampling temperature (0.0-2.0)
            max_output_tokens: Maximum tokens in response
            **kwargs: Additional provider-specific parameters

        Returns:
            Response text
        """
        model = model or self.default_model
        return self._call_api(
            model=model,
            messages=messages,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            **kwargs,
        )
