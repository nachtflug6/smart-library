from smart_library.domain.entities.page import Page

def parse_pages(struct):
    facsimile = struct.get("facsimile")
    pages = []
    page_map = {}
    if facsimile and facsimile.surfaces:
        for surface in facsimile.surfaces:
            page = Page(
                page_number=surface.page,
                # ... other fields ...
                texts=[],
            )
            pages.append(page)
            page_map[surface.page] = page
    return pages, page_map