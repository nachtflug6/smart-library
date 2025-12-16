def parse_pages(struct, page_service=None):
    facsimile = struct.get("facsimile")
    num_pages = 0

    if facsimile is None:
        return num_pages

    surfaces = getattr(facsimile, "surfaces", None)
    if surfaces:
        try:
            num_pages = len(surfaces)
        except Exception:
            # fallback if surfaces is not sized
            num_pages = 0

    return num_pages