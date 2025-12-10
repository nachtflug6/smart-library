import unittest
import nltk
from smart_library.utils.chunker import TextChunker
from smart_library.config import ChunkerConfig

# Ensure NLTK punkt is available for sentence splitting
nltk.download('punkt', quiet=True)

class TestTextChunker(unittest.TestCase):
    def setUp(self):
        self.chunker = TextChunker()

    def test_order_and_logic(self):
        # Sample input: 3 chunks, 1 too short, 1 too long, 1 just right
        chunks = [
            "Short.",  # too short, should merge
            "This is a medium length chunk. It should remain as is.",
            "This is a very long chunk. " + "Sentence. " * 50  # too long, should split
        ]

        non_overlap, overlap = self.chunker.process_chunks(chunks)

        # Check order preserved
        self.assertEqual(len(non_overlap), len(overlap))
        for i in range(len(non_overlap)):
            self.assertIn(non_overlap[i], overlap[i])

        # Check merging: first chunk should be merged with second
        self.assertTrue("Short." in non_overlap[0])
        self.assertTrue("medium length chunk" in non_overlap[0])

        # Check splitting: last chunk should be split
        self.assertTrue(any(len(chunk) <= self.chunker.max_char for chunk in non_overlap))

        # Check overlap: each chunk (except first) should start with a sentence from previous chunk
        for i in range(1, len(overlap)):
            prev_sentences = nltk.sent_tokenize(non_overlap[i-1])
            overlap_sents = prev_sentences[-self.chunker.overlap:] if len(prev_sentences) >= self.chunker.overlap else prev_sentences
            overlap_text = " ".join(overlap_sents)
            self.assertTrue(overlap[i].startswith(overlap_text))

if __name__ == "__main__":
    unittest.main()