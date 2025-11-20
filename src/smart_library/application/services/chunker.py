from typing import List
import re


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

        # Normalize newlines
        text = text.strip().replace("\r\n", "\n")

        # Split on sentence boundaries if possible
        sentences = self._split_into_sentences(text)

        chunks = []
        current = ""

        for sentence in sentences:
            # If adding the next sentence fits -> append
            if len(current) + len(sentence) <= self.max_chars:
                current += sentence
            else:
                # Finalize this chunk
                if current:
                    chunks.append(current.strip())

                # Start new chunk
                # If sentence alone is massive → hard cut
                if len(sentence) > self.max_chars:
                    chunks.extend(self._hard_split(sentence))
                    current = ""
                else:
                    current = sentence

        # Add last chunk
        if current:
            chunks.append(current.strip())

        # Add overlap if needed
        return self._apply_overlap(chunks)

    # -------------------------
    # Helpers
    # -------------------------

    def _split_into_sentences(self, text: str) -> List[str]:
        """Basic sentence splitter using regex."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s + " " for s in sentences if s.strip()]

    def _hard_split(self, long_text: str) -> List[str]:
        """Hard split for extremely long sentences or tables."""
        return [
            long_text[i : i + self.max_chars]
            for i in range(0, len(long_text), self.max_chars)
        ]

    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        if self.overlap == 0 or len(chunks) <= 1:
            return chunks

        overlapped = []
        for i, chunk in enumerate(chunks):
            if i == 0:
                overlapped.append(chunk)
                continue

            prev = chunks[i - 1]
            tail = prev[-self.overlap:]
            combined = tail + " " + chunk
            overlapped.append(combined)

        return overlapped
