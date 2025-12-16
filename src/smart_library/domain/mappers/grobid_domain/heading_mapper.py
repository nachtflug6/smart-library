from smart_library.domain.mappers.grobid_domain.text_mapper import parse_texts
from smart_library.domain.mappers.grobid_domain.utils import extract_page_number_from_coords
from smart_library.domain.services.text_service import TextService
from smart_library.domain.services.heading_service import HeadingService
from smart_library.domain.services.relationship_service import RelationshipService
from smart_library.domain.constants.relationship_types import RelationshipType
import logging

logger = logging.getLogger(__name__)

def parse_headings(struct, document_id, text_service=None, relationship_service=None, start_heading_index=0, start_text_index=0):
    body = struct.get("body")
    headings = []
    texts = []

    # Use default TextService if not provided
    if text_service is None:
        text_service = TextService.default_instance()

    # Heading service for creating heading entities
    heading_service = HeadingService.default_instance()

    heading_index = start_heading_index
    text_index = start_text_index
    relationships = []

    relationship_service = relationship_service or RelationshipService.default_instance()

    if body and getattr(body, "sections", None):
        sections = getattr(body, "sections", []) or []
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("total_top_sections=%d", len(sections))
        for section_idx, section in enumerate(sections):
            section_title = getattr(section, "title", None)

            page_number = extract_page_number_from_coords(getattr(section, "coords", None))

            heading_obj = None
            if section_title:
                heading_obj = heading_service.create_heading(
                    title=section_title,
                    index=heading_index,
                    page_number=page_number if page_number is not None else 0,
                    parent_id=document_id,
                    metadata={"document_id": document_id},
                )
                headings.append(heading_obj)
                heading_index += 1
                # Heading -> document relationship
                try:
                    rel_h = relationship_service.create_relationship(
                        source_id=heading_obj.id,
                        target_id=document_id,
                        type=RelationshipType.BELONGS_TO,
                        metadata={"document_id": document_id},
                    )
                    relationships.append(rel_h)
                except Exception:
                    pass

            # Paragraphs in section -> parse_texts with global text index
            paras, text_index, rels = parse_texts(
                section,
                heading_obj,
                document_id,
                text_service=text_service,
                relationship_service=relationship_service,
                start_index=text_index,
            )
            texts.extend(paras)
            if rels:
                relationships.extend(rels)

    return headings, texts, heading_index, text_index, relationships