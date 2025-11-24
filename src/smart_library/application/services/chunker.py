import re
from typing import List


class TextChunker:
    """
    Simple, reliable, deterministic text chunker.
    Splits text into chunks of approx `max_chars` with optional overlap.
    """

    def __init__(self, max_chars: int = 1000, overlap: int = 100):
        assert max_chars > overlap, "max_chars must be > overlap"
        self.max_chars = max_chars
        self.overlap = overlap

    def chunk(self, text: str) -> List[str]:
        if not text:
            return []

        text = text.strip().replace("\r\n", "\n")
        sentences = self._split_into_sentences(text)

        chunks = []
        current = ""

        for sentence in sentences:
            if len(current) + len(sentence) <= self.max_chars:
                current += sentence
            else:
                if current:
                    chunks.append(current)
                # If sentence is too long, hard split it
                if len(sentence) > self.max_chars:
                    chunks.extend(self._hard_split(sentence))
                    current = ""
                else:
                    current = sentence
        if current:
            chunks.append(current)

        return self._apply_overlap(chunks)

    def _split_into_sentences(self, text: str) -> List[str]:
        # Split on punctuation followed by whitespace, preserving punctuation
        sentences = re.findall(r'[^.!?]*[.!?]', text)
        return [s.strip() for s in sentences if s.strip()]

    def _hard_split(self, long_text: str) -> List[str]:
        return [
            long_text[i : i + self.max_chars]
            for i in range(0, len(long_text), self.max_chars)
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
