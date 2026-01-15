from smart_library.infrastructure.repositories.vector_repository import VectorRepository


class VectorService:
    """
    Service for vector storage, retrieval, and similarity search.
    Uses sqlite-vec virtual table; vector id is the rowid (should match entity id).
    """
    def __init__(self, repo=None):
        self.repo = repo or VectorRepository.default_instance()

    def add_vector(self, id, vector, created_by=None):
        return self.repo.add_vector(id, vector, created_by)

    def get_vector(self, id):
        return self.repo.get_vector(id)

    def search_similar_vectors(self, query_vector, top_k=10):
        return self.repo.search_similar_vectors(query_vector, top_k=top_k)

    def delete_vector(self, id):
        return self.repo.delete_vector(id)

    def list_vectors(self):
        return self.repo.list_vectors()

    def cleanup_orphaned_vectors(self):
        return self.repo.cleanup_orphaned_vectors()
