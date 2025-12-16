from smart_library.domain.services.document_service import DocumentService
from smart_library.domain.mappers.grobid_domain.page_mapper import parse_pages
from types import SimpleNamespace

def parse_document(struct, source_path=None, source_url=None, file_hash=None,
                   document_service=None):
    header = struct.get("header") or SimpleNamespace()

    # Use default DocumentService if not provided
    document_service = document_service or DocumentService.default_instance()

    # Parse pages and build page map
    num_pages = parse_pages(struct)

    # Create Document using service (only pass recognized Document fields)
    doc = document_service.create_document(
        title=getattr(header, "title", None),
        authors=[f"{a.first_name or ''} {a.last_name or ''}".strip() for a in getattr(header, "authors", [])],
        doi=getattr(header, "doi", None),
        publication_date=getattr(header, "published_date", None),
        publisher=getattr(header, "publisher", None),
        abstract=getattr(header, "abstract", None),
        file_hash=file_hash,
        source_path=source_path,
        source_url=source_url,
        page_count=num_pages,
    )

    return doc