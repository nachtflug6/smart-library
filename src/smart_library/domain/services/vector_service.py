from smart_library.infrastructure.repositories.vector_repository import VectorRepository

class VectorService:
    """
    Service for vector storage, retrieval, and similarity search.
    """
    def __init__(self, repo=None):
        self.repo = repo or VectorRepository.default_instance()

    def add_vector(self, id, vector, model, dim):
        return self.repo.add_vector(id, vector, model, dim)

    def get_vector(self, id):
        return self.repo.get_vector(id)

    def delete_vector(self, id):
        return self.repo.delete_vector(id)

    def list_vectors(self):
        return self.repo.list_vectors()
