"""
Base LLM client interface.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    def __init__(self, api_key: str, default_model: str):
        """
        Initialize LLM client.

        Args:
            api_key: API key for the LLM service
            default_model: Default model to use
        """
        self.api_key = api_key
        self.default_model = default_model

    @abstractmethod
    def _call_api(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_output_tokens: int,
        **kwargs,
    ) -> str:
        """
        Call the LLM API.

        Args:
            model: Model name
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_output_tokens: Maximum tokens in response
            **kwargs: Additional provider-specific parameters

        Returns:
            Response text
        """
        pass

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
