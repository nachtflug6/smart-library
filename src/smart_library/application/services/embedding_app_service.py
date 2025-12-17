from smart_library.infrastructure.embeddings.embedding_service import EmbeddingService


class EmbeddingAppService:
    def __init__(self, svc: EmbeddingService = None):
        self.svc = svc or EmbeddingService()

    def embed(self, text: str):
        return self.svc.embed(text)
