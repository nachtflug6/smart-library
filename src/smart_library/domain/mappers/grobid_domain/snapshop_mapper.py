
from smart_library.domain.aggregates.document_snapshot import DocumentSnapshot
from smart_library.domain.mappers.grobid_domain.document_mapper import parse_document
from smart_library.domain.mappers.grobid_domain.heading_mapper import parse_headings
from smart_library.domain.services.document_service import DocumentService
from smart_library.domain.services.heading_service import HeadingService
from smart_library.domain.services.text_service import TextService
from smart_library.domain.services.relationship_service import RelationshipService
from smart_library.domain.services.term_service import TermService
# No direct constant imports required here; relationship types are created by
# the relationship service within lower-level mappers (heading/text mappers).


def build_snapshot(struct, source_path=None, source_url=None, file_hash=None,
				   document_service=None, heading_service=None,
				   text_service=None, relationship_service=None, term_service=None):
	"""Build a DocumentSnapshot from a grobid `struct` using domain services.

	- Creates the `Document` via `parse_document`/DocumentService.
	- Creates Heading and Text entities using services and links them with Relationships.
	- Attaches `document_id` in each object's `metadata`.
	"""
	# Services (use defaults if not provided)
	document_service = document_service or DocumentService.default_instance()
	heading_service = heading_service or HeadingService.default_instance()
	text_service = text_service or TextService.default_instance()
	relationship_service = relationship_service or RelationshipService.default_instance()
	term_service = term_service or TermService.default_instance()

	# Create document
	document = parse_document(struct, source_path=source_path, source_url=source_url, file_hash=file_hash,
							  document_service=document_service)

	headings = []
	texts = []
	relationships = []
	terms = []

	body = struct.get("body")
	if not body:
		return DocumentSnapshot(document=document, texts=texts, headings=headings, relationships=relationships, terms=terms)

	# Delegate parsing of headings and texts (and relationships) to mapper helpers
	# `parse_headings` will create headings, texts and relationships using the
	# provided services and return them for inclusion in the snapshot.
	headings, texts, heading_index, text_index, rels = parse_headings(
		struct,
		document.id,
		text_service=text_service,
		relationship_service=relationship_service,
		start_heading_index=0,
		start_text_index=0,
	)
	relationships.extend(rels or [])

	# (Terms extraction is out of scope here) — keep empty list or extend if available

	return DocumentSnapshot(document=document, texts=texts, headings=headings, relationships=relationships, terms=terms)

