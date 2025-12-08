from smart_library.domain.entities.text import Text
from smart_library.domain.constants.text_types import TextType
from smart_library.infrastructure.parsers.utils import extract_page_number_from_coords

def parse_paragraphs(section, section_text_obj, page_map):
    paragraph_texts = []
    for para_idx, para in enumerate(section.paragraphs):
        # Use utility to get page number from coords
        page_number = extract_page_number_from_coords(getattr(para, "coords", None))
        if page_number is None and hasattr(para, "page"):
            page_number = para.page

        page_obj = page_map.get(page_number)
        page_id = getattr(page_obj, "id", None) if page_obj else None

        norm_text = getattr(para, "text", None)
        if norm_text is None and hasattr(para, "content"):
            norm_text = para.content

        para_text_obj = Text(
            title=None,
            content=norm_text,
            character_count=len(norm_text) if norm_text else 0,
            text_type=TextType.PARAGRAPH,
            document_id=None,  # will set later
            page_id=page_id,
            parent_id=getattr(section_text_obj, "id", None) if section_text_obj else None,
            index=para_idx,
        )

        paragraph_texts.append(para_text_obj)
        if page_obj:
            page_obj.texts.append(para_text_obj)
    return paragraph_texts