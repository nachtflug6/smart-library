from smart_library.utils.chunker import TextChunker

def test_chunker_basic_split():
    chunker = TextChunker(max_chars=20, overlap=5)
    text = "This is sentence one. This is sentence two! And this is sentence three?"
    chunks = chunker.chunk(text)
    assert len(chunks) >= 2
    assert all(isinstance(c, str) for c in chunks)
    assert "sentence one." in chunks[0]
    assert "sentence two!" in "".join(chunks)
    assert "sentence three?" in "".join(chunks)

def test_chunker_empty_text():
    chunker = TextChunker(max_chars=20, overlap=5)
    assert chunker.chunk("") == []

def test_chunker_hard_split():
    chunker = TextChunker(max_chars=10, overlap=0)
    long_text = "A" * 25
    chunks = chunker.chunk(long_text)
    assert len(chunks) == 3
    assert all(len(c) <= 10 for c in chunks)

def test_chunker_overlap():
    chunker = TextChunker(max_chars=15, overlap=5)
    text = "First sentence. Second sentence. Third sentence."
    chunks = chunker.chunk(text)
    assert len(chunks) > 1
    for i in range(1, len(chunks)):
        # Check that the overlap is present at the start of each chunk
        assert chunks[i].startswith(chunks[i-1][-5:])

def test_chunker_sentence_splitter():
    chunker = TextChunker(max_chars=100, overlap=5)
    text = "Hello world! How are you? I'm fine."
    sentences = chunker._split_into_sentences(text)
    assert len(sentences) == 3
    assert sentences[0].strip().endswith("!")
    assert sentences[1].strip().endswith("?")
    assert sentences[2].strip().endswith(".")