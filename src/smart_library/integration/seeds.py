"""
Reusable seed datasets for integration tests.
"""

def seed_vectors(vector_service):
    """Seed the vector service with a small set of vectors."""
    vectors = [
        ("vecA", [0.0, 0.0, 1.0]),
        ("vecB", [1.0, 0.0, 0.0]),
        ("vecC", [0.0, 1.0, 0.0]),
    ]
    for vid, vec in vectors:
        vector_service.add_vector(vid, vec)
