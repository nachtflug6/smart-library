from smart_library.domain.services.document_service import DocumentService
from smart_library.domain.services.page_service import PageService
from smart_library.domain.services.text_service import TextService
from .page import parse_pages
from .section import parse_sections

def parse_document(struct, source_path=None, source_url=None, file_hash=None,
                   document_service=None, page_service=None, text_service=None):
    header = struct.get("header")

    # Use default services if not provided
    document_service = document_service or DocumentService.default_instance()
    page_service = page_service or PageService.default_instance()
    text_service = text_service or TextService.default_instance()

    # Parse pages and build page map
    pages, page_map = parse_pages(struct, page_service=page_service)

    # Parse sections and paragraphs, passing text_service
    section_texts, paragraph_texts = parse_sections(struct, page_map, text_service=text_service)

    # Create Document using service
    doc = document_service.create_document(
        title=getattr(header, "title", None),
        authors=[f"{a.first_name or ''} {a.last_name or ''}".strip() for a in getattr(header, "authors", [])],
        keywords=getattr(header, "keywords", None),
        doi=getattr(header, "doi", None),
        publication_date=getattr(header, "published_date", None),
        publisher=getattr(header, "publisher", None),
        abstract=getattr(header, "abstract", None),
        file_hash=file_hash,
        source_path=source_path,
        source_url=source_url,
        page_count=len(pages),
        pages=pages,
        texts=section_texts + paragraph_texts,
    )

    doc_id = getattr(doc, "id", None)

    # Assign document_id and parent_id for pages and texts at creation time if possible
    for page in doc.pages:
        page.document_id = doc_id
        page.parent_id = doc_id

    for text in doc.texts:
        text.document_id = doc_id
        # Section logic
        if getattr(text, "text_type", None) == "section":
            text.parent_id = doc_id
        # Paragraph logic
        elif getattr(text, "text_type", None) == "paragraph":
            if not getattr(text, "parent_id", None):
                possible_sections = [
                    s for s in section_texts
                    if getattr(s, "page_id", None) == getattr(text, "page_id", None)
                ]
                if len(possible_sections) == 1:
                    text.parent_id = getattr(possible_sections[0], "id", None)
            if not getattr(text, "parent_id", None):
                text.parent_id = doc_id
        else:
            text.parent_id = doc_id

    return doc