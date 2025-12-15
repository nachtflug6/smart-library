
from smart_library.infrastructure.embeddings.embedding_service import EmbeddingService
from smart_library.application.services.vector_service import VectorService

class SearchService:
	def __init__(self, embedding_service=None, vector_service=None):
		self.embedding_service = embedding_service or EmbeddingService()
		self.vector_service = vector_service or VectorService()

	def similarity_search(self, text, top_k=10):
		"""
		1. Embed the input text to a vector
		2. Perform vector similarity search
		Returns: list of similar vectors (with ids and scores)
		"""
		embedding = self.embedding_service.embed(text)
		return self.vector_service.search_similar_vectors(embedding, top_k=top_k)
