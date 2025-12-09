from smart_library.config import MIN_PARAGRAPH_LENGTH
from smart_library.domain.entities.text import Text
from smart_library.domain.constants.text_types import TextType
from smart_library.infrastructure.parsers.utils import extract_page_number_from_coords

def parse_paragraphs(section, section_text_obj, page_map):
    paragraph_texts = []
    merged_paragraphs = []
    i = 0
    paras = section.paragraphs
    while i < len(paras):
        para = paras[i]
        # Use utility to get page number from coords
        page_number = extract_page_number_from_coords(getattr(para, "coords", None))
        if page_number is None and hasattr(para, "page"):
            page_number = para.page

        page_obj = page_map.get(page_number)
        page_id = getattr(page_obj, "id", None) if page_obj else None

        norm_text = getattr(para, "text", None)
        if norm_text is None and hasattr(para, "content"):
            norm_text = para.content

        # Merge logic
        merged_text = norm_text or ""
        merged_count = len(merged_text)
        j = i
        while merged_count < MIN_PARAGRAPH_LENGTH and j + 1 < len(paras):
            next_para = paras[j + 1]
            next_page_number = extract_page_number_from_coords(getattr(next_para, "coords", None))
            if next_page_number is None and hasattr(next_para, "page"):
                next_page_number = next_para.page
            if next_page_number != page_number:
                break
            next_text = getattr(next_para, "text", None)
            if next_text is None and hasattr(next_para, "content"):
                next_text = next_para.content
            merged_text += " " + (next_text or "")
            merged_count = len(merged_text)
            j += 1

        para_text_obj = Text(
            title=None,
            content=merged_text,
            character_count=merged_count,
            text_type=TextType.PARAGRAPH,
            document_id=None,  # will set later
            page_id=page_id,
            parent_id=getattr(section_text_obj, "id", None) if section_text_obj else None,
            index=i,
        )

        paragraph_texts.append(para_text_obj)
        if page_obj:
            page_obj.texts.append(para_text_obj)
        i = j + 1
    return paragraph_texts