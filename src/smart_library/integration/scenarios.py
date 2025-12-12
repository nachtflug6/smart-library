"""
Integration scenarios: end-to-end behavior probes using the integration context.
"""
from .context import make_context


def scenario_vector_similarity():
    ctx = make_context()
    # Add a few vectors
    vectors = [
        ("vec1", [0.1, 0.2, 0.3]),
        ("vec2", [0.2, 0.1, 0.4]),
        ("vec3", [0.9, 0.8, 0.7]),
    ]
    for vid, vec in vectors:
        ctx.vector_service.add_vector(vid, vec)
    # Query
    query = [0.1, 0.2, 0.3]
    results = ctx.vector_service.search_similar_vectors(query, top_k=2)
    print("Scenario: Vector similarity search results:")
    for res in results:
        print(res)

# Add more scenarios as needed
