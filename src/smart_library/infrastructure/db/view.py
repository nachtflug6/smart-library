import sqlite3

def view_page(document_id: str, page: int):
    db = sqlite3.connect("db/smart_library.db")
    cur = db.cursor()

    row = cur.execute("""
        SELECT path 
        FROM pages
        WHERE document_id = ? AND page = ?
    """, (document_id, page)).fetchone()

    if not row:
        print(f"[error] page {page} not found for {document_id}")
        return

    path = row[0]

    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"[error] file missing: {path}")
        return

    print(f"=== {document_id} — Page {page} ===\n")
    print(text)
