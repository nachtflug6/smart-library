"""Generic extractor for LLM-based extraction with on-call user prompt and verification."""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Tuple
import re

from smart_library.llm.client import LLMClient
from smart_library.utils.parsing import parse_structured_obj
from smart_library.utils.textmatch import verify_string_in_string


class BaseExtractor:
    """
    Generic LLM extractor.

    - System and user prompts are provided per call (strings or callables).
    - No subclass prompts or normalization.
    - Parses JSON output and optionally verifies every string/primitive against source text.
      If verification is enabled and a value cannot be verified, it is set to None.
    """

    def __init__(
        self,
        client: LLMClient,
        *,
        model: str = "gpt-4o-mini",
        temperature: float = 1.0,
        max_output_tokens: int = 4096,
        enforce_json: bool = True,
    ):
        self.client = client
        self.model = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.enforce_json = enforce_json

    # ------------------------------- internals --------------------------------

    def _build_messages(
        self,
        text: str,
        system_prompt: str | None,
        user_prompt: str,
    ) -> List[Dict[str, str]]:
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Combine user prompt with the document text
        messages.append({
            "role": "user",
            "content": f"{user_prompt}\n\n{text}"
        })
        
        return messages

    def _chat(self, messages: List[Dict[str, str]], **kwargs) -> Tuple[Any | None, str | None]:
        extras = dict(kwargs or {})
        if self.enforce_json:
            extras["response_format"] = {"type": "json_object"}
        try:
            raw = self.client.chat(
                messages,
                model=self.model,
                temperature=self.temperature,
                max_output_tokens=self.max_output_tokens,
                **extras,
            )
            return parse_structured_obj(raw)
        except Exception as e:
            return None, f"llm_error: {e}"

    def _tokenize_and_normalize(self, value: str) -> List[str]:
        """
        Split a string into tokens and normalize them.
        Handles punctuation, whitespace, and common separators.
        Filters out single-character tokens.
        """
        # Split on common separators: commas, semicolons, whitespace, pipes, etc.
        tokens = re.split(r'[,;|\s]+', value)
        # Normalize: strip, lowercase, remove empty, filter out single chars
        normalized = [t.strip().lower() for t in tokens if t.strip() and len(t.strip()) >= 2]
        return normalized

    def _verify_value(
        self,
        value: str,
        text: str,
        *,
        fuzzy: bool,
        tolerance: int,
        token_threshold: float,
    ) -> bool:
        """
        Verify a string value by tokenizing and checking each token.
        Returns True if verified_tokens/total_tokens >= token_threshold.
        Single-character tokens are ignored.
        """
        tokens = self._tokenize_and_normalize(value)
        if not tokens:
            # If no tokens remain after filtering, accept the value
            return True
        
        verified_count = 0
        for token in tokens:
            if verify_string_in_string(token, text, fuzzy=fuzzy, tolerance=tolerance):
                verified_count += 1
        
        verification_ratio = verified_count / len(tokens)
        return verification_ratio >= token_threshold

    def _nullify_unverified(
        self,
        data: Any,
        text: str,
        *,
        fuzzy: bool,
        tolerance: int,
        token_threshold: float,
    ) -> Any:
        """
        Return a deep-copied structure where any string/primitive value that
        cannot be verified in the source text is replaced with None.
        
        For strings, splits into tokens (min 2 chars) and verifies each token individually.
        A value is kept if verified_tokens/total_tokens >= token_threshold.
        """
        def check(v: Any) -> Any:
            # None stays None
            if v is None:
                return None
            
            # Strings: tokenize and verify
            if isinstance(v, str):
                return v if self._verify_value(
                    v, text, 
                    fuzzy=fuzzy, 
                    tolerance=tolerance,
                    token_threshold=token_threshold
                ) else None
            
            # Primitives: convert to string and verify
            if isinstance(v, (int, float, bool)):
                sv = str(v)
                return v if self._verify_value(
                    sv, text,
                    fuzzy=fuzzy,
                    tolerance=tolerance,
                    token_threshold=token_threshold
                ) else None
            
            # Dict: recurse
            if isinstance(v, dict):
                return {k: check(val) for k, val in v.items()}
            
            # List/Tuple: recurse element-wise (keep shape)
            if isinstance(v, (list, tuple)):
                mapped = [check(x) for x in v]
                return mapped if isinstance(v, list) else tuple(mapped)
            
            # Other types: leave as-is (cannot verify)
            return v

        return check(data)

    # --------------------------------- API ------------------------------------

    def extract_one(
        self,
        text: str,
        *,
        system_prompt: str | Callable[[str], str] | None = None,
        user_prompt: str | Callable[[str], str],
        verify: bool = True,
        fuzzy: bool = True,
        tolerance: int = 80,
        token_threshold: float = 0.5,
        **chat_kwargs,
    ) -> Dict[str, Any] | List[Any]:
        """
        Run one extraction call:
        - Sends system and user messages built from prompts.
        - Expects JSON output; parses it.
        - Optionally verifies values against source text and nullifies unverified ones.

        Args:
            text: Source text to extract from
            system_prompt: Optional system prompt string or callable(text) -> string
            user_prompt: User prompt string or callable(text) -> string
            verify: If True, verify extracted values against source text
            fuzzy: Use fuzzy matching for verification
            tolerance: Fuzzy match tolerance (0-100) for individual token matching
            token_threshold: Minimum ratio of verified tokens (0.0-1.0) to accept a value
            **chat_kwargs: Additional arguments passed to client.chat
        """
        if not text or not text.strip():
            return {"error": "empty_text"}

        messages = self._build_messages(text, system_prompt, user_prompt)
        data, reason = self._chat(messages, **chat_kwargs)
        if data is None:
            return {"error": "invalid_response", "why": reason}

        if verify:
            return self._nullify_unverified(
                data, text,
                fuzzy=fuzzy,
                tolerance=tolerance,
                token_threshold=token_threshold
            )
        return data

    def extract_bulk(
        self,
        texts: Dict[str, str],
        *,
        system_prompt: str | Callable[[str], str] | None = None,
        user_prompt: str | Callable[[str], str],
        verify: bool = True,
        fuzzy: bool = True,
        tolerance: int = 80,
        token_threshold: float = 0.5,
        **chat_kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Sequential bulk processing (one API call per item_id).
        Returns a list of {"item_id": ..., "data": ...} or {"item_id": ..., "error": ...}.

        Args:
            texts: Dict mapping item_id to source text
            system_prompt: Optional system prompt string or callable(text) -> string
            user_prompt: User prompt string or callable(text) -> string
            verify: If True, verify extracted values against source text
            fuzzy: Use fuzzy matching for verification
            tolerance: Fuzzy match tolerance (0-100) for individual token matching
            token_threshold: Minimum ratio of verified tokens (0.0-1.0) to accept a value
            **chat_kwargs: Additional arguments passed to client.chat
        """
        results: List[Dict[str, Any]] = []
        for item_id, text in texts.items():
            out = self.extract_one(
                text,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                verify=verify,
                fuzzy=fuzzy,
                tolerance=tolerance,
                token_threshold=token_threshold,
                **chat_kwargs,
            )
            if isinstance(out, dict) and "error" in out:
                results.append({"item_id": item_id, **out})
            else:
                results.append({"item_id": item_id, "data": out})
        return results