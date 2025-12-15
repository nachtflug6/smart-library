from smart_library.domain.entities.text import Text
from smart_library.domain.constants.text_types import TextType
from smart_library.domain.mappers.grobid_domain.text_mapper import parse_texts
from smart_library.domain.mappers.grobid_domain.utils import extract_page_number_from_coords
from smart_library.domain.services.text_service import TextService
from smart_library.domain.services.heading_service import HeadingService

def parse_headings(struct, document_id, text_service=None):
    body = struct.get("body")
    headings = []
    texts = []

    # Use default TextService if not provided
    if text_service is None:
        text_service = TextService.default_instance()

    # Heading service for creating heading entities
    heading_service = HeadingService.default_instance()

    if body and body.sections:
        for section_idx, section in enumerate(body.sections):
            section_title = getattr(section, "title", None)

            page_number = extract_page_number_from_coords(getattr(section, "coords", None))

            if section_title:
                heading_obj = heading_service.create_heading(
                    title=section_title,
                    index=section_idx,
                    page_number=page_number if page_number is not None else 0,
                    parent_id=document_id,
                    metadata={"document_id": document_id},
                )
                headings.append(heading_obj)

            # Paragraphs in section (already chunked in parse_paragraphs)
                paras = parse_texts(section, heading_obj, document_id, text_service=text_service)
                texts.extend(paras)

            return headings, texts