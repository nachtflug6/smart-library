
from smart_library.domain.aggregates.document_snapshot import DocumentSnapshot
from smart_library.domain.mappers.grobid_domain.document_mapper import parse_document
from smart_library.domain.mappers.grobid_domain.heading_mapper import parse_headings
from smart_library.domain.mappers.grobid_domain.text_mapper import parse_texts
from smart_library.domain.services.document_service import DocumentService
from smart_library.domain.services.heading_service import HeadingService
from smart_library.domain.services.text_service import TextService
from smart_library.domain.services.relationship_service import RelationshipService
from smart_library.domain.services.term_service import TermService
from smart_library.domain.constants.relationship_types import RelationshipType
from smart_library.domain.constants.text_types import TextType


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

	# Iterate sections -> headings + texts
	for section_idx, section in enumerate(getattr(body, "sections", []) or []):
		title = getattr(section, "title", None)
		page_number = None
		# try coords if available
		coords = getattr(section, "coords", None)
		if coords is not None and hasattr(coords, "page"):
			page_number = getattr(coords, "page")

		heading_kwargs = {
			"title": title,
			"index": section_idx,
			"page_number": page_number if page_number is not None else 0,
			"parent_id": document.id,
			"metadata": {"document_id": document.id},
		}
		if title:
			heading = heading_service.create_heading(**heading_kwargs)
			headings.append(heading)
		else:
			heading = None

		# paragraphs -> texts
		for para_idx, para in enumerate(getattr(section, "paragraphs", []) or []):
			content = getattr(para, "text", None) or getattr(para, "content", "")
			text_kwargs = {
				"content": content,
				"display_content": content,
				"embedding_content": content,
				"text_type": TextType.PARAGRAPH,
				"index": para_idx,
				"parent_id": document.id,
				"metadata": {"document_id": document.id},
			}
			text = text_service.create_text(**text_kwargs)
			texts.append(text)

			# Relationships: text -> heading (UNDER_HEADING) and text -> document (BELONGS_TO)
			if heading is not None:
				rel1 = relationship_service.create_relationship(
					source_id=text.id,
					target_id=heading.id,
					type=RelationshipType.UNDER_HEADING,
					metadata={"document_id": document.id},
				)
				relationships.append(rel1)

			rel2 = relationship_service.create_relationship(
				source_id=text.id,
				target_id=document.id,
				type=RelationshipType.BELONGS_TO,
				metadata={"document_id": document.id},
			)
			relationships.append(rel2)

		# Heading -> document relationship (if heading created)
		if heading is not None:
			rel_h = relationship_service.create_relationship(
				source_id=heading.id,
				target_id=document.id,
				type=RelationshipType.BELONGS_TO,
				metadata={"document_id": document.id},
			)
			relationships.append(rel_h)

	# (Terms extraction is out of scope here) — keep empty list or extend if available

	return DocumentSnapshot(document=document, texts=texts, headings=headings, relationships=relationships, terms=terms)

