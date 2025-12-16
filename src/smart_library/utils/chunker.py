import re
from typing import List
from smart_library.config import ChunkerConfig

class TextChunker:
    """
    Simple, reliable, deterministic text chunker.
    Splits text into chunks of approx `max_char` with optional overlap.
    """

    def __init__(self):
        self.min_char = ChunkerConfig.MIN_CHAR
        self.max_char = ChunkerConfig.MAX_CHAR
        self.overlap = ChunkerConfig.OVERLAP
        assert self.max_char > self.overlap, "max_char must be > overlap"

    # --- PUBLIC API ---------------------------------------------------------

    def chunk(self, text: str) -> list[str]:
        """
        Chunk a single long text string into non-overlapping chunks.
        """
        if not text:
            return []

        text = text.strip().replace("\r\n", "\n")
        sentences = self._split_into_sentences(text)
        return self._build_chunks_from_sentences(sentences)

    def normalize_chunks(self, chunks: list[str]) -> list[str]:
        """
        Take an existing list of strings (e.g., paragraphs) and normalize them
        into chunks between min_char and max_char, using the same logic as
        `chunk()`. This will happily merge/split across original boundaries.
        """
        all_sentences: list[str] = []
        for ch in chunks:
            all_sentences.extend(self._split_into_sentences(ch))
        return self._build_chunks_from_sentences(all_sentences)

    def process_chunks(self, chunks: list[str]) -> tuple[list[str], list[str]]:
        """
        Returns (non_overlap_chunks, overlap_chunks).
        - non_overlap_chunks: merged/split to fit min_char/max_char.
        - overlap_chunks: each chunk includes overlap (by sentences) from previous chunk.
        """
        non_overlap_chunks = self.normalize_chunks(chunks)

        # Step 2: Apply sentence-based overlap
        if self.overlap == 0 or len(non_overlap_chunks) <= 1:
            return non_overlap_chunks, non_overlap_chunks

        overlap_chunks: list[str] = [non_overlap_chunks[0]]
        for i in range(1, len(non_overlap_chunks)):
            prev = non_overlap_chunks[i - 1]
            curr = non_overlap_chunks[i]
            prev_sentences = self._split_into_sentences(prev)
            # Treat `self.overlap` as a character-length overlap (config value in chars).
            # Collect sentences from the end of the previous chunk until we reach
            # approximately `self.overlap` characters, or include all sentences.
            if self.overlap <= 0:
                overlap_sents = []
            else:
                overlap_sents = []
                total = 0
                for s in reversed(prev_sentences):
                    overlap_sents.insert(0, s)
                    total += len(s) + 1
                    if total >= self.overlap:
                        break
            overlap_text = " ".join(overlap_sents).strip()
            if overlap_text:
                overlap_chunks.append(overlap_text + " " + curr)
            else:
                overlap_chunks.append(curr)

        return non_overlap_chunks, overlap_chunks

    # --- HELPERS -----------------------------------------------------------

    def _split_into_sentences(self, text: str) -> list[str]:
        """
        Split text into sentences using punctuation (., ?, !) as delimiters.
        Keeps all sentences; does not discard short ones.
        """
        text = re.sub(r'\s+', ' ', text.strip())
        if not text:
            return []

        parts = re.split(r'([.!?])', text)
        sentences: list[str] = []
        current = ""

        for part in parts:
            if not part:
                continue
            current += part
            if part in ".!?":
                s = current.strip()
                if s:
                    sentences.append(s)
                current = ""

        if current.strip():
            sentences.append(current.strip())

        return sentences

    def _hard_split(self, long_text: str) -> list[str]:
        """
        Split long_text into chunks of at most max_char, but never split words.
        """
        chunks: list[str] = []
        start = 0
        text_len = len(long_text)
        while start < text_len:
            end = min(start + self.max_char, text_len)
            if end < text_len:
                space = long_text.rfind(" ", start, end)
                if space > start:
                    end = space
            chunk = long_text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end
            while start < text_len and long_text[start].isspace():
                start += 1
        return chunks

    def _build_chunks_from_sentences(self, sentences: list[str]) -> list[str]:
        """
        Group sentences into chunks between min_char and max_char,
        aiming for lengths near the midpoint.
        """
        units: list[str] = []
        for s in sentences:
            s = s.strip()
            if not s:
                continue
            if len(s) <= self.max_char:
                units.append(s)
            else:
                units.extend(self._hard_split(s))

        if not units:
            return []

        target = (self.min_char + self.max_char) // 2
        chunks: list[str] = []
        current: list[str] = []
        current_len = 0

        for u in units:
            u_len = len(u)
            if not current:
                current = [u]
                current_len = u_len
                continue

            new_len = current_len + 1 + u_len

            if new_len > self.max_char:
                chunks.append(" ".join(current))
                current = [u]
                current_len = u_len
                continue

            if current_len < self.min_char:
                current.append(u)
                current_len = new_len
            else:
                dist_keep = abs(current_len - target)
                dist_add = abs(new_len - target)
                if dist_add <= dist_keep:
                    current.append(u)
                    current_len = new_len
                else:
                    chunks.append(" ".join(current))
                    current = [u]
                    current_len = u_len

        if current:
            chunks.append(" ".join(current))

        if len(chunks) >= 2 and len(chunks[-1]) < self.min_char:
            if len(chunks[-2]) + 1 + len(chunks[-1]) <= self.max_char:
                chunks[-2] = chunks[-2] + " " + chunks[-1]
                chunks.pop()

        return chunks
