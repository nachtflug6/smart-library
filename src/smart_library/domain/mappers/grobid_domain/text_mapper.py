from smart_library.domain.constants.text_types import TextType
from smart_library.domain.mappers.grobid_domain.utils import extract_page_number_from_coords

from smart_library.utils.chunker import TextChunker
import logging
from smart_library.domain.services.text_service import TextService
from smart_library.domain.services.relationship_service import RelationshipService
from smart_library.domain.constants.relationship_types import RelationshipType


def parse_texts(section, section_text_obj, document_id, text_service=None, relationship_service=None, start_index=0):
    """Parse paragraphs from a section and create Text domain objects.

    Groups paragraphs by page *number* (no page objects) and uses
    `TextService.create_text` to build domain `Text` objects. Each Text will
    include `document_id` in its metadata when provided.
    """
    paragraph_texts = []
    relationships = []
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

    logger = logging.getLogger(__name__)
    chunker = TextChunker()
    for page_number, paragraphs in paras_by_page.items():
        # Concatenate all paragraph texts for this page number
        page_text = "\n".join(p for p in paragraphs if p)
        if not page_text:
            continue
        # Debug: log paragraph counts and lengths before chunking
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("page=%s paragraphs=%d", page_number, len(paragraphs))
            for i, p in enumerate(paragraphs):
                if not p:
                    logger.debug(" para[%d] length=0 (empty)", i)
                else:
                    logger.debug(" para[%d] length=%d", i, len(p))
        # Chunk the text using paragraph-aware normalization from the chunker config
        page_paragraphs = [p for p in paragraphs if p]
        non_overlap_chunks, overlap_chunks = chunker.process_chunks(page_paragraphs)
        # Debug: log chunk counts and lengths after chunking
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(" chunks_non_overlap=%d chunks_with_overlap=%d", len(non_overlap_chunks), len(overlap_chunks))
            for i, ch in enumerate(non_overlap_chunks):
                logger.debug("  chunk[%d] length=%d", i, len(ch))
        # Relationship service for creating relationships between texts/headings/document
        relationship_service = relationship_service or RelationshipService.default_instance()

        for idx, (non_overlap, overlap) in enumerate(zip(non_overlap_chunks, overlap_chunks)):
            global_idx = start_index + idx
            # Attach document and page number to text metadata so downstream
            # presentation code can show page information.
            meta = {"document_id": document_id}
            if page_number is not None:
                meta["page_number"] = page_number

            text_obj = text_service.create_text(
                content=non_overlap,
                display_content=non_overlap,
                embedding_content=overlap,
                text_type=TextType.PARAGRAPH,
                parent_id=document_id,
                index=global_idx,
                character_count=len(non_overlap) if non_overlap is not None else 0,
                page_number=page_number,
                metadata=meta,
            )
            paragraph_texts.append(text_obj)
            # Create relationships: text -> heading (UNDER_HEADING) and text -> document (BELONGS_TO)
            try:
                if section_text_obj is not None:
                    rel1 = relationship_service.create_relationship(
                        source_id=text_obj.id,
                        target_id=section_text_obj.id,
                        type=RelationshipType.UNDER_HEADING,
                        metadata={"document_id": document_id},
                    )
                    relationships.append(rel1)
                rel2 = relationship_service.create_relationship(
                    source_id=text_obj.id,
                    target_id=document_id,
                    type=RelationshipType.BELONGS_TO,
                    metadata={"document_id": document_id},
                )
                relationships.append(rel2)
            except Exception:
                # relationship creation is best-effort here
                pass
        # advance start_index by number of chunks produced for this page
        start_index += len(non_overlap_chunks)

    return paragraph_texts, start_index, relationships