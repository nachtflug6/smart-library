def print_document(doc, indent=0):
    prefix = " " * indent
    print(f"{prefix}Document: {getattr(doc, 'title', None)} (id={getattr(doc, 'id', None)})")
    print(f"{prefix}  Authors: {getattr(doc, 'authors', None)}")
    print(f"{prefix}  Pages: {len(getattr(doc, 'pages', []))}")

    # Orphan texts: no page_id
    orphan_texts = [t for t in getattr(doc, 'texts', []) if getattr(t, 'page_id', None) is None]
    print(f"{prefix}  Orphan Texts: {len(orphan_texts)}")
    for t in sorted(orphan_texts, key=lambda x: (getattr(x, 'text_type', ''), getattr(x, 'index', -1))):
        if getattr(t, 'text_type', None) == "section":
            print(f"{prefix}    [Orphan Section] {t.title} (index={getattr(t, 'index', None)}, id={getattr(t, 'id', None)})")
        elif getattr(t, 'text_type', None) == "paragraph":
            print(f"{prefix}    [Orphan Paragraph] {repr(t.content)[:120]}... (index={getattr(t, 'index', None)}, id={getattr(t, 'id', None)})")
        else:
            print(f"{prefix}    [Orphan Text] {t.text_type}: {repr(t.content)[:120]}... (index={getattr(t, 'index', None)}, id={getattr(t, 'id', None)})")

    # Print all by page
    for p in sorted(getattr(doc, 'pages', []), key=lambda x: getattr(x, 'page_number', 0)):
        print(f"{prefix}  Page {getattr(p, 'page_number', None)} (id={getattr(p, 'id', None)}):")
        # Get all texts for this page, sorted by index
        page_texts = [t for t in getattr(doc, 'texts', []) if getattr(t, 'page_id', None) == getattr(p, 'id', None)]
        page_sections = [t for t in page_texts if getattr(t, 'text_type', None) == "section"]
        page_paragraphs = [t for t in page_texts if getattr(t, 'text_type', None) == "paragraph"]

        for section in sorted(page_sections, key=lambda x: getattr(x, 'index', -1)):
            print(f"{prefix}    [Section] {section.title} (index={getattr(section, 'index', None)}, id={getattr(section, 'id', None)})")
            # Print paragraphs under this section, sorted by index
            section_paragraphs = [para for para in page_paragraphs if getattr(para, 'parent_id', None) == getattr(section, 'id', None)]
            for para in sorted(section_paragraphs, key=lambda x: getattr(x, 'index', -1)):
                print(f"{prefix}      [Paragraph] {repr(para.content)}... (index={getattr(para, 'index', None)}, id={getattr(para, 'id', None)})")
        # Print paragraphs not under any section
        unsectioned_paragraphs = [para for para in page_paragraphs if getattr(para, 'parent_id', None) not in [getattr(s, 'id', None) for s in page_sections]]
        for para in sorted(unsectioned_paragraphs, key=lambda x: getattr(x, 'index', -1)):
            print(f"{prefix}    [Paragraph] {repr(para.content)}... (index={getattr(para, 'index', None)}, id={getattr(para, 'id', None)})")