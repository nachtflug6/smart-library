import pytest
from smart_library.config import OllamaConfig
from smart_library.application.llm.ollama_client import OllamaClient, OllamaEmbeddingModel

@pytest.mark.integration
def test_ollama_generate_basic():
    client = OllamaClient(
        url=OllamaConfig.GENERATE_URL,
        model=OllamaConfig.GENERATION_MODEL
    )
    prompt = "Say hello in one sentence."
    response = client.generate(prompt)
    assert isinstance(response, str)
    assert len(response.strip()) > 0
    assert "hello" in response.lower()

@pytest.mark.integration
def test_ollama_embedding_basic():
    embedder = OllamaEmbeddingModel(
        url=OllamaConfig.EMBEDDING_URL,
        model=OllamaConfig.EMBEDDING_MODEL
    )
    text = "hello world"
    embedding = embedder.embed(text)
    assert isinstance(embedding, list)
    assert all(isinstance(x, float) for x in embedding)
    assert len(embedding) > 0