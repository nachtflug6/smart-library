import re
from typing import List
from smart_library.config import CHUNKER_CONFIG


class TextChunker:
    """
    Simple, reliable, deterministic text chunker.
    Splits text into chunks of approx `max_chars` with optional overlap.
    """

    def __init__(
        self,
        max_tokens: int = None,
        overlap: int = None
    ):
        # Use config defaults if not provided
        max_tokens = max_tokens if max_tokens is not None else CHUNKER_CONFIG.get("max_tokens", 1000)
        overlap = overlap if overlap is not None else CHUNKER_CONFIG.get("overlap", 100)
        assert max_tokens > overlap, "max_tokens must be > overlap"
        self.max_tokens = max_tokens
        self.overlap = overlap

    def chunk(self, text: str) -> List[str]:
        if not text:
            return []

        text = text.strip().replace("\r\n", "\n")
        sentences = self._split_into_sentences(text)

        chunks = []
        current = ""

        for sentence in sentences:
            if len(current) + len(sentence) <= self.max_tokens:
                current += sentence
            else:
                if current:
                    chunks.append(current)
                # If sentence is too long, hard split it
                if len(sentence) > self.max_tokens:
                    chunks.extend(self._hard_split(sentence))
                    current = ""
                else:
                    current = sentence
        if current:
            chunks.append(current)

        return self._apply_overlap(chunks)

    def _split_into_sentences(self, text: str) -> List[str]:
        # Split on punctuation followed by whitespace, preserving punctuation
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if s.strip()]

    def _hard_split(self, long_text: str) -> List[str]:
        return [
            long_text[i : i + self.max_tokens]
            for i in range(0, len(long_text), self.max_tokens)
        ]

    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        if self.overlap == 0 or len(chunks) <= 1:
            return chunks

        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev = overlapped[-1]
            overlap_text = prev[-self.overlap:] if len(prev) >= self.overlap else prev
            # Prepend overlap to current chunk
            overlapped.append(overlap_text + chunks[i])
        return overlapped
