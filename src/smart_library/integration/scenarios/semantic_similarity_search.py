
from smart_library.application.services.index_service import IndexService
from smart_library.application.services.search_service import SearchService
from smart_library.domain.services.document_service import DocumentService
from smart_library.domain.services.page_service import PageService

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

	print("""
============================================================
				SEMANTIC SIMILARITY SEARCH
============================================================
Goal: Find which stored texts are most similar to the query below.

Query:
	"{}"

------------------- Ranked Results -------------------------
| Rank |      ID       | Cosine Sim. | Text Snippet
------------------------------------------------------------""".format(search_text))
	text_service = index_service.text_service
	for rank, res in enumerate(results, 1):
		text_obj = text_service.get_text(res['id'])
		text_content = text_obj.content if text_obj else "<not found>"
		snippet = (text_content[:60] + ("..." if len(text_content) > 60 else ""))
		print(f"|  {rank:<3} | {res['id'][:10]}... |   {res['cosine_similarity']:.4f}   | {snippet}")
	print("============================================================\n")

	# Optionally, assert that the most similar is a dog/puppy text
	# (This depends on the embedding model quality)
	# assert results[0]['id'] in ids[:2]
