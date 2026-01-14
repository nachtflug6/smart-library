from smart_library.domain.services.document_service import DocumentService
from smart_library.domain.mappers.grobid_domain.page_mapper import parse_pages
from types import SimpleNamespace
import re

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

    # Extract year from published_date if available
    published_date = getattr(header, "published_date", None)
    year = None
    if published_date:
        # Try to extract a 4-digit year from the date string
        year_match = re.search(r'\b(19|20)\d{2}\b', str(published_date))
        if year_match:
            try:
                year = int(year_match.group(0))
            except ValueError:
                year = None

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