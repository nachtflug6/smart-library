
import pytest
from smart_library.infrastructure.repositories.vector_repository import VectorRepository
import numpy as np

@pytest.fixture(scope="module")
def repo():
    # Use default instance (assumes test DB is set up)
    return VectorRepository.default_instance()

@pytest.fixture(scope="function")
def test_vectors():
    # Example vectors (3D)
    return [
        ("vec1", [1.0, 0.0, 0.0], "test_model", 3),
        ("vec2", [0.0, 1.0, 0.0], "test_model", 3),
        ("vec3", [0.0, 0.0, 1.0], "test_model", 3),
        ("vec4", [1.0, 1.0, 0.0], "test_model", 3),
    ]


def test_add_and_search_vectors(repo, test_vectors):
    # Add vectors
    for vid, vec, model, dim in test_vectors:
        repo.add_vector(vid, vec, model, dim)

    # Query vector close to vec4
    query = [0.9, 0.9, 0.0]
    results = repo.search_similar_vectors(query, top_k=2, metric='cosine', model="test_model")
    assert len(results) == 2
    # vec4 should be most similar
    assert results[0]['id'] == "vec4"
    # vec1 or vec2 should be next
    assert results[1]['id'] in ["vec1", "vec2"]

    # Clean up
    for vid, _, _, _ in test_vectors:
        repo.delete_vector(vid)
    # Ensure deleted
    for vid, _, _, _ in test_vectors:
        assert repo.get_vector(vid) is None
