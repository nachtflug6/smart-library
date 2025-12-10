from smart_library.domain.entities.text import Text
from smart_library.domain.constants.text_types import TextType
from smart_library.infrastructure.parsers.utils import extract_page_number_from_coords
from smart_library.utils.chunker import TextChunker

def parse_paragraphs(section, section_text_obj, page_map):
    paragraph_texts = []
    paras = section.paragraphs

    # Group paragraphs by page_id
    from collections import defaultdict
    paras_by_page = defaultdict(list)
    for para in paras:
        page_number = extract_page_number_from_coords(getattr(para, "coords", None))
        if page_number is None and hasattr(para, "page"):
            page_number = para.page
        page_obj = page_map.get(page_number)
        page_id = getattr(page_obj, "id", None) if page_obj else None

        norm_text = getattr(para, "text", None)
        if norm_text is None and hasattr(para, "content"):
            norm_text = para.content

        paras_by_page[page_id].append((norm_text or "", page_id, page_obj))

    chunker = TextChunker()
    for page_id, para_tuples in paras_by_page.items():
        # Concatenate all paragraph texts for this page
        page_text = "\n".join(t[0] for t in para_tuples if t[0])
        # Chunk the text
        non_overlap_chunks, overlap_chunks = chunker.process_chunks([page_text])
        for idx, (non_overlap, overlap) in enumerate(zip(non_overlap_chunks, overlap_chunks)):
            para_text_obj = Text(
                title=None,
                content=non_overlap,
                display_content=non_overlap,
                embedding_content=overlap,
                text_type=TextType.PARAGRAPH,
                document_id=None,  # will set later
                page_id=page_id,
                parent_id=getattr(section_text_obj, "id", None) if section_text_obj else None,
                index=idx,
            )
            paragraph_texts.append(para_text_obj)
            # Optionally add to page_obj.texts if needed
            if para_tuples[0][2]:
                para_tuples[0][2].texts.append(para_text_obj)

    return paragraph_texts