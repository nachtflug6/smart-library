import sqlite3
import os
import re

def search(query: str, ignore_case: bool = True):
    db = sqlite3.connect("db/smart_library.db")
    cur = db.cursor()

    flags = re.IGNORECASE if ignore_case else 0
    pattern = re.compile(re.escape(query), flags)

    rows = cur.execute("""
        SELECT document_id, page, path 
        FROM pages
        ORDER BY document_id, page
    """).fetchall()

    hits = []

    for doc_id, page, path in rows:
        if not os.path.exists(path):
            continue

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        if pattern.search(text):
            # short preview
            snippet = text.strip().replace("\n", " ")
            snippet = snippet[:200] + "..." if len(snippet) > 200 else snippet

            hits.append((doc_id, page, snippet))

    if not hits:
        print("[no results]")
        return

    for doc_id, page, snippet in hits:
        print(f"{doc_id:20}  p{page:03d}  {snippet}")
