from .page import parse_pages
from .section import parse_sections
from .paragraph import parse_paragraphs
from smart_library.domain.entities.document import Document

def parse_document(struct, source_path=None, source_url=None, file_hash=None):
    header = struct.get("header")
    pages, page_map = parse_pages(struct)
    section_texts, paragraph_texts = parse_sections(struct, page_map)

    doc = Document(
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

    # Set document_id and parent_id for all pages
    for page in doc.pages:
        page.document_id = doc_id
        page.parent_id = doc_id

    # Build a map from section id to section object for parent assignment
    section_id_map = {getattr(section, "id", None): section for section in section_texts}

    # Set document_id, page_id, parent_id for all texts
    for text in doc.texts:
        text.document_id = doc_id
        # Section logic
        if getattr(text, "text_type", None) == "section":
            text.parent_id = doc_id
        # Paragraph logic
        elif getattr(text, "text_type", None) == "paragraph":
            # parent_id should be the section's id if available
            # If not set, try to find the section by page_id and index
            if not getattr(text, "parent_id", None):
                # Try to find the section on the same page
                possible_sections = [
                    s for s in section_texts
                    if getattr(s, "page_id", None) == getattr(text, "page_id", None)
                ]
                # If only one section on the page, assign it
                if len(possible_sections) == 1:
                    text.parent_id = getattr(possible_sections[0], "id", None)
                # Otherwise, leave as None (will be orphan)
            # If still not set, fallback to doc
            if not getattr(text, "parent_id", None):
                text.parent_id = doc_id
        else:
            text.parent_id = doc_id

    return doc