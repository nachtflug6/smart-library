from smart_library.domain.entities.text import Text
from smart_library.domain.constants.text_types import TextType
from smart_library.domain.mappers.grobid_domain.utils import extract_page_number_from_coords

from smart_library.utils.chunker import TextChunker
from smart_library.domain.services.text_service import TextService


def parse_texts(section, section_text_obj, document_id, text_service=None):
    """Parse paragraphs from a section and create Text domain objects.

    Groups paragraphs by page *number* (no page objects) and uses
    `TextService.create_text` to build domain `Text` objects. Each Text will
    include `document_id` in its metadata when provided.
    """
    paragraph_texts = []
    paras = getattr(section, "paragraphs", []) or []

    # Use default TextService if not provided
    if text_service is None:
        text_service = TextService.default_instance()

    # Group paragraphs by page number
    from collections import defaultdict
    paras_by_page = defaultdict(list)
    for para in paras:
        page_number = extract_page_number_from_coords(getattr(para, "coords", None))
        if page_number is None and hasattr(para, "page"):
            page_number = getattr(para, "page")

        norm_text = getattr(para, "text", None)
        if norm_text is None and hasattr(para, "content"):
            norm_text = getattr(para, "content")

        paras_by_page[page_number].append(norm_text or "")

    chunker = TextChunker()
    for page_number, paragraphs in paras_by_page.items():
        # Concatenate all paragraph texts for this page number
        page_text = "\n".join(p for p in paragraphs if p)
        if not page_text:
            continue
        # Chunk the text
        non_overlap_chunks, overlap_chunks = chunker.process_chunks([page_text])
        for idx, (non_overlap, overlap) in enumerate(zip(non_overlap_chunks, overlap_chunks)):
            text_obj = text_service.create_text(
                content=non_overlap,
                display_content=non_overlap,
                embedding_content=overlap,
                text_type=TextType.PARAGRAPH,
                parent_id=document_id,
                index=idx,
                metadata={"document_id": document_id} if document_id is not None else {},
            )
            paragraph_texts.append(text_obj)

    return paragraph_texts