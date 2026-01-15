
from smart_library.infrastructure.embeddings.embedding_service import EmbeddingService
from smart_library.application.services.vector_service import VectorService
from smart_library.application.services.text_app_service import TextAppService

class SearchService:
	def __init__(self, embedding_service=None, vector_service=None, text_service=None):
		self.embedding_service = embedding_service or EmbeddingService()
		self.vector_service = vector_service or VectorService()
		self.text_service = text_service or TextAppService()

	def similarity_search(self, text, top_k=10):
		"""
		1. Embed the input text to a vector
		2. Perform vector similarity search
		Returns: list of similar vectors (with ids and scores)
		"""
		embedding = self.embedding_service.embed(text)
		return self.vector_service.search_similar_vectors(embedding, top_k=top_k)

	def cleanup_orphaned_vectors(self):
		"""
		Remove vectors that have no corresponding text entity.
		Useful for cleaning up after document deletions.
		"""
		vector_ids = self.vector_service.repo.list_vectors()
		deleted_count = 0
		
		for vector_id in vector_ids:
			try:
				text = self.text_service.get_text(vector_id)
				if not text:
					# Vector has no corresponding text, delete it
					self.vector_service.delete_vector(vector_id)
					deleted_count += 1
			except Exception:
				# Entity doesn't exist, delete the vector
				self.vector_service.delete_vector(vector_id)
				deleted_count += 1
		
		return deleted_count
