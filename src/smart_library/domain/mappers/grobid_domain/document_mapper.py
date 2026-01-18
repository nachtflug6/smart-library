from smart_library.domain.services.document_service import DocumentService
from smart_library.domain.mappers.grobid_domain.page_mapper import parse_pages
from types import SimpleNamespace
import re
from smart_library.infrastructure.doi.doi_parser import extract_year_from_doi

def _format_author_name(author):
    """Format author as 'LastName, FirstName MiddleInitials'."""
    last = author.last_name or ""
    first = author.first_name or ""
    middle_initials = " ".join(f"{m[0]}." for m in (author.middle_names or []) if m)
    
    if first and middle_initials:
        return f"{last}, {first} {middle_initials}".strip()
    elif first:
        return f"{last}, {first}".strip()
    else:
        return last


def parse_document(struct, source_path=None, source_url=None, file_hash=None,
                   document_service=None):
    header = struct.get("header") or SimpleNamespace()

    # Use default DocumentService if not provided
    document_service = document_service or DocumentService.default_instance()

    # Parse pages and build page map
    num_pages = parse_pages(struct)

    # Extract year with multiple fallback options
    year = None
    
    # Try published_date first (from publicationStmt)
    published_date = getattr(header, "published_date", None)
    if published_date:
        year_match = re.search(r'\b(19|20)\d{2}\b', str(published_date))
        if year_match:
            try:
                year = int(year_match.group(0))
            except ValueError:
                pass
    
    # Fallback 1: Try imprint_date (from monogr/imprint)
    if year is None:
        imprint_date = getattr(header, "imprint_date", None)
        if imprint_date:
            year_match = re.search(r'\b(19|20)\d{2}\b', str(imprint_date))
            if year_match:
                try:
                    year = int(year_match.group(0))
                except ValueError:
                    pass
    
    # Fallback 2: Try to extract year from DOI patterns (more reliable than text search)
    if year is None:
        doi = getattr(header, "doi", None)
        if doi:
            year = extract_year_from_doi(doi)

    # Create Document using service (only pass recognized Document fields)
    doc = document_service.create_document(
        title=getattr(header, "title", None),
        authors=[_format_author_name(a) for a in getattr(header, "authors", [])],
        doi=getattr(header, "doi", None),
        publication_date=published_date,
        publisher=getattr(header, "publisher", None),
        year=year,
        abstract=getattr(header, "abstract", None),
        file_hash=file_hash,
        source_path=source_path,
        source_url=source_url,
        page_count=num_pages,
    )

    return doc
