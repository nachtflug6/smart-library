

from smart_library.application.services.index_service import IndexService
from smart_library.application.services.search_service import SearchService
from smart_library.domain.services.document_service import DocumentService
from smart_library.domain.services.page_service import PageService
from .utils import print_scenario_header, print_scenario_footer, print_scenario_table_header, print_scenario_table_row

def scenario_semantic_similarity_search(context):
	# Setup: create services
	index_service = IndexService()
	search_service = SearchService()


	# Create a dummy document using index_service
	doc_id = index_service.index_document(title="Dummy Document")

	# Input texts (semantically related, not keyword identical)
	texts = [
		"A dog is playing in the park.",
		"Children are running with a puppy on the grass.",
		"A cat is sleeping on the sofa.",
		"People are walking their pets in the garden.",
		"Birds are singing in the trees."
	]

	# Index the texts, using the document as parent
	ids = []
	for t in texts:
		text_id, _ = index_service.index_text(t, parent_id=doc_id)
		ids.append(text_id)

	# Search text (semantically close to some, not keyword identical)
	search_text = "A canine enjoys outdoor activities."


	# Perform similarity search
	results = search_service.similarity_search(search_text, top_k=5)

	print_scenario_header("Semantic Similarity Search", goal=f"Find which stored texts are most similar to the query below.\n\nQuery:\n    \"{search_text}\"")
	print_scenario_table_header(["Rank", "ID", "Cosine Sim.", "Text Snippet"])
	text_service = index_service.text_service
	for rank, res in enumerate(results, 1):
		text_obj = text_service.get_text(res['id'])
		text_content = text_obj.content if text_obj else "<not found>"
		snippet = (text_content[:60] + ("..." if len(text_content) > 60 else ""))
		print_scenario_table_row([f"{rank:<3}", f"{res['id'][:10]}...", f"{res['cosine_similarity']:.4f}", snippet])
	print_scenario_footer()

	# Optionally, assert that the most similar is a dog/puppy text
	# (This depends on the embedding model quality)
	# assert results[0]['id'] in ids[:2]
