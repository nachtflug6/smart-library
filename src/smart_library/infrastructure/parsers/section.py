from smart_library.domain.entities.text import Text
from smart_library.domain.constants.text_types import TextType
from .paragraph import parse_paragraphs
from smart_library.infrastructure.parsers.utils import extract_page_number_from_coords

def parse_sections(struct, page_map):
    body = struct.get("body")
    section_texts = []
    paragraph_texts = []
    if body and body.sections:
        for section_idx, section in enumerate(body.sections):
            section_title = getattr(section, "title", None)
            section_text_obj = None
            page_id = None

            page_number = extract_page_number_from_coords(getattr(section, "coords", None))
            if page_number is not None:
                page_obj = page_map.get(page_number)
                page_id = getattr(page_obj, "id", None) if page_obj else None

            if section_title:
                section_text_obj = Text(
                    title=section_title,
                    content=section_title,
                    text_type=TextType.SECTION,
                    document_id=None,
                    page_id=page_id,
                    parent_id=None,
                    index=section_idx,
                )
                section_texts.append(section_text_obj)

            # Paragraphs in section (already chunked in parse_paragraphs)
            paras = parse_paragraphs(section, section_text_obj, page_map)
            paragraph_texts.extend(paras)

    return section_texts, paragraph_texts