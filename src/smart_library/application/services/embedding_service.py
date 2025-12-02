from smart_library.application.llm.ollama_client import OllamaEmbeddingModel
from smart_library.infrastructure.repositories.embedding_repository import EmbeddingRepository
from smart_library.application.services.text_service import TextService
from smart_library.config import OllamaConfig
from smart_library.domain.entities.embedding import Embedding
import numpy as np

class EmbeddingService:
    def __init__(self, llm_client, embedding_repo, text_repo):
        self.llm = llm_client          # talks to Ollama
        self.embeddings = embedding_repo
        self.texts = text_repo

    def embed_text(self, text_id: str):
        text = self.texts.get_text(text_id)
        vector = self.llm.embed(text.content)
        embedding = Embedding(
            id=f"{text_id}:{OllamaConfig.EMBEDDING_MODEL}",
            vector=vector,
            parent_id=text_id,
            model=OllamaConfig.EMBEDDING_MODEL,
            metadata={}
        )
        self.embeddings.add(embedding)

    def embed_document(self, doc_id: str):
        chunks = self.texts.get_all_for_document(doc_id)
        for t in chunks:
            self.embed_text(t.id)

    def aggregate_to_page_embedding(self, page_id: str, chunk_ids: list):
        """
        Aggregate chunk embeddings to create a page embedding (e.g., by averaging).
        """
        vectors = []
        for chunk_id in chunk_ids:
            embedding = self.embeddings.get_for_parent(chunk_id)
            if embedding is not None and embedding.vector is not None:
                vectors.append(embedding.vector)
        if not vectors:
            return None
        avg_vector = np.mean(np.array(vectors), axis=0).tolist()
        # Save the aggregated embedding as a new Embedding object
        page_embedding = Embedding(
            id=f"{page_id}:{OllamaConfig.EMBEDDING_MODEL}",
            vector=avg_vector,
            parent_id=page_id,
            model=OllamaConfig.EMBEDDING_MODEL,
            metadata={}
        )
        self.embeddings.add(page_embedding)
        return avg_vector

    def aggregate_to_document_embedding(self, doc_id: str, page_ids: list):
        """
        Aggregate page embeddings to create a document embedding (e.g., by averaging).
        """
        vectors = []
        for page_id in page_ids:
            embedding = self.embeddings.get_for_parent(page_id)
            if embedding is not None and embedding.vector is not None:
                vectors.append(embedding.vector)
        if not vectors:
            return None
        avg_vector = np.mean(np.array(vectors), axis=0).tolist()
        # Save the aggregated embedding as a new Embedding object
        doc_embedding = Embedding(
            id=f"{doc_id}:{OllamaConfig.EMBEDDING_MODEL}",
            vector=avg_vector,
            parent_id=doc_id,
            model=OllamaConfig.EMBEDDING_MODEL,
            metadata={}
        )
        self.embeddings.add(doc_embedding)
        return avg_vector

    @classmethod
    def default_instance(cls):
        embedding_repo = EmbeddingRepository.default_instance()
        text_service = TextService.default_instance()
        llm_client = OllamaEmbeddingModel(
            url=OllamaConfig.EMBEDDING_URL,
            model=OllamaConfig.EMBEDDING_MODEL
        )
        return cls(llm_client=llm_client, embedding_repo=embedding_repo, text_repo=text_service)
