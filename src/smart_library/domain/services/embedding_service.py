from smart_library.infrastructure.llm.clients.ollama_client import OllamaEmbeddingModel
from smart_library.domain.services.vector_service import VectorService
from smart_library.domain.services.text_service import TextService
from smart_library.config import OllamaConfig
from smart_library.domain.entities.embedding import Embedding
import numpy as np

class EmbeddingService:
    def __init__(self, llm_client, vector_service, text_repo):
        self.llm = llm_client          # talks to Ollama
        self.vectors = vector_service
        self.texts = text_repo

    def embed_text(self, text_id: str):
        text = self.texts.get_text(text_id)
        vector = self.llm.embed(text.content)
        emb_id = f"{text_id}:{OllamaConfig.EMBEDDING_MODEL}"
        self.vectors.add_vector(emb_id, vector, OllamaConfig.EMBEDDING_MODEL, len(vector))

    def embed_document(self, doc):
        """
        Embed all texts in the document, updating or creating embeddings as needed.
        Optionally, aggregate to page and document embeddings.
        """
        for page in getattr(doc, "pages", []):
            self.embed_page(page)
        # Optionally, aggregate page embeddings to document embedding
        page_ids = [getattr(page, "id", None) for page in getattr(doc, "pages", []) if getattr(page, "id", None)]
        self.aggregate_to_document_embedding(getattr(doc, "id", None), page_ids)

    def embed_page(self, page):
        """
        Embed all texts in a page, updating or creating embeddings as needed.
        Optionally, aggregate to page embedding.
        """
        chunk_ids = []
        for text in getattr(page, "texts", []):
            emb_id = self.embed_text_object(text)
            if emb_id:
                chunk_ids.append(emb_id)
        # Optionally, aggregate chunk embeddings to page embedding
        self.aggregate_to_page_embedding(getattr(page, "id", None), chunk_ids)

    def embed_text_object(self, text):
        """
        Embed a single text object, updating or creating the embedding as needed.
        Returns the embedding id.
        """
        text_id = getattr(text, "id", None)
        if not text_id:
            return None
        content = getattr(text, "embedding_content", None) or getattr(text, "content", None)
        if not content:
            return None

        # Check if embedding exists
        embedding = self.embeddings.get_for_parent(text_id)
        if embedding is not None:
            # Update if content has changed
            if embedding.metadata.get("content_hash") != hash(content):
                vector = self.llm.embed(content)
                embedding.vector = vector
                embedding.metadata["content_hash"] = hash(content)
                self.embeddings.update(embedding)
        else:
            # Create new embedding
            vector = self.llm.embed(content)
            from smart_library.domain.entities.embedding import Embedding
            embedding = Embedding(
                id=f"{text_id}:{self.llm.model}",
                vector=vector,
                parent_id=text_id,
                model=self.llm.model,
                metadata={"content_hash": hash(content)}
            )
            self.embeddings.add(embedding)
        return embedding.id if embedding else None

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
        vector_service = VectorService()
        text_service = TextService.default_instance()
        llm_client = OllamaEmbeddingModel(
            url=OllamaConfig.EMBEDDING_URL,
            model=OllamaConfig.EMBEDDING_MODEL
        )
        return cls(llm_client=llm_client, vector_service=vector_service, text_repo=text_service)

    @staticmethod
    def create_embedding(id, vector, parent_id, model, metadata=None):
        """
        Factory for creating an Embedding object. Add validation/normalization here if needed.
        """
        from smart_library.domain.entities.embedding import Embedding
        return Embedding(
            id=id,
            vector=vector,
            parent_id=parent_id,
            model=model,
            metadata=metadata or {}
        )
