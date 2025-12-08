from smart_library.domain.entities.document import Document
from smart_library.domain.entities.page import Page
from smart_library.domain.entities.text import Text
from smart_library.infrastructure.parsers.utils import ContentNormaliser

def parse_grobid_struct_to_domain(struct, source_path=None, source_url=None, file_hash=None):
    header = struct.get("header")
    facsimile = struct.get("facsimile")
    body = struct.get("body")

    normaliser = ContentNormaliser()

    # --- Pages ---
    pages = []
    page_map = {}  # page_number -> Page
    if facsimile and facsimile.surfaces:
        for surface in facsimile.surfaces:
            page = Page(
                page_number=surface.page,
                document_id=None,  # will set later
                parent_id=None,    # will set later
                texts=[],
            )
            pages.append(page)
            page_map[surface.page] = page

    # --- Texts ---
    orphan_texts = []
    section_texts = []
    if body and body.sections:
        for section in body.sections:
            # Section title as Text
            section_title = getattr(section, "title", None)
            section_text_obj = None
            if section_title:
                section_text_obj = Text(
                    title=section_title,
                    content=section_title,
                    text_type="section",
                    document_id=None,  # will set later
                    page_id=None,
                    parent_id=None,
                )
                section_texts.append(section_text_obj)

            # Paragraphs in section
            for para in section.paragraphs:
                page_number = None
                if para.coords and hasattr(para.coords, "boxes"):
                    pages_list = [box.page for box in para.coords.boxes if hasattr(box, "page")]
                    if pages_list:
                        page_number = pages_list[0]
                elif hasattr(para, "page"):
                    page_number = para.page

                norm_text = normaliser.normalize(para.text).content

                para_text_obj = Text(
                    title=None,
                    content=norm_text,
                    text_type="paragraph",
                    document_id=None,  # will set later
                    page_id=None,
                    parent_id=None,
                )

                # Set parent_id to section_text_obj if available
                if section_text_obj:
                    para_text_obj.parent_id = getattr(section_text_obj, "id", None)

                if page_number and page_number in page_map:
                    page_obj = page_map[page_number]
                    para_text_obj.page_id = getattr(page_obj, "id", None)
                    para_text_obj.document_id = None  # will set later
                    page_obj.texts.append(para_text_obj)
                else:
                    para_text_obj.document_id = None  # will set later
                    orphan_texts.append(para_text_obj)

    # --- Document ---
    doc = Document(
        title=header.title,
        authors=[f"{a.first_name or ''} {a.last_name or ''}".strip() for a in header.authors],
        keywords=header.keywords,
        doi=header.doi,
        publication_date=header.published_date,
        publisher=header.publisher,
        abstract=header.abstract,
        file_hash=file_hash,
        source_path=source_path,
        source_url=source_url,
        page_count=len(pages),
        pages=pages,
        texts=section_texts + orphan_texts,
    )

    # Set document_id and parent_id for all pages and texts
    doc_id = getattr(doc, "id", None)
    for page in doc.pages:
        page.document_id = doc_id
        page.parent_id = doc_id
        for text in getattr(page, "texts", []):
            text.document_id = doc_id
            # If text is a paragraph, parent_id is section id if available
            if text.text_type == "paragraph" and text.parent_id:
                pass  # already set above
            else:
                text.parent_id = page.id if hasattr(page, "id") else None
    for text in doc.texts:
        text.document_id = doc_id
        if text.text_type == "section":
            text.parent_id = doc_id
        else:
            text.parent_id = doc_id

    return doc