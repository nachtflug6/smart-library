"""
Integration test: add and search 768-dim float vectors using VectorService.
"""

import numpy as np
from smart_library.integration.context import make_context
import traceback
from .utils import print_scenario_header, print_scenario_footer, print_scenario_table_header, print_scenario_table_row

def scenario_vector_similarity_search(context):
    """
    Professional integration test for adding and searching 768-dim float vectors.
    Ensures correct storage and similarity search in VectorService.
    """
    np.random.seed(123)
    dim = 768
    vector_service = context.vector_service
    try:
        # Seed 5 reproducible 768-dim vectors
        vectors = [
            (f"vec{i+1}", np.random.rand(dim).tolist())
            for i in range(5)
        ]
        for vid, vec in vectors:
            vector_service.add_vector(vid, vec)

        # Query with a new random 768-dim vector
        query = np.random.rand(dim).tolist()
        top_k = 3
        results = vector_service.search_similar_vectors(query, top_k=top_k)

        print_scenario_header("Vector Similarity Search", goal=f"Find which stored 768-dim vectors are most similar to a random query vector.\n\nQuery vector: shape=({dim}) [seed=123]\nSeeded vectors: {[vid for vid, _ in vectors]}")
        print_scenario_table_header(["Rank", "ID", "Cosine Sim.", "Distance"])
        for i, res in enumerate(results, 1):
            vid = res.get("id") if isinstance(res, dict) else res[0]
            score = res.get("cosine_similarity")
            distance = res.get("distance")
            print_scenario_table_row([f"{i:<3}", f"{vid[:10]}...", f"{score:.4f}", f"{distance:.4f}"])
        print_scenario_footer()

        # Assertions: correct number of results, ids in seeded
        assert len(results) == top_k, f"Expected {top_k} results, got {len(results)}"
        result_ids = [res.get("id") if isinstance(res, dict) else res[0] for res in results]
        for rid in result_ids:
            assert rid in [v[0] for v in vectors], f"Unexpected result id: {rid}"
        print("[PASS] test_add_and_search_768d_vectors: Results as expected.")
    except Exception as e:
        print("[FAIL] test_add_and_search_768d_vectors: Exception occurred.")
        traceback.print_exc()
    finally:
        context.cleanup()


