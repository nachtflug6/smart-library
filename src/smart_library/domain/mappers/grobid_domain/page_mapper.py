def parse_pages(struct, page_service=None):
    facsimile = struct.get("facsimile")

    if facsimile and facsimile.surfaces:
        num_pages = len(facsimile.surfaces)
        
    return num_pages