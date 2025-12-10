from smart_library.domain.services.page_service import PageService

def parse_pages(struct, page_service=None):
    facsimile = struct.get("facsimile")
    pages = []
    page_map = {}

    # Use default PageService if not provided
    if page_service is None:
        page_service = PageService()

    if facsimile and facsimile.surfaces:
        for surface in facsimile.surfaces:
            page = page_service.create_page(
                page_number=surface.page,
                # ... other fields from surface ...
                texts=[],
            )
            pages.append(page)
            page_map[surface.page] = page
    return pages, page_map