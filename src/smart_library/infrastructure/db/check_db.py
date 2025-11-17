import os
import sqlite3

def check_db(db_path="db/smart_library.db"):
    results = []

    # 1. Connect to DB
    if not os.path.exists(db_path):
        return "ERROR: Database file does not exist."

    db = sqlite3.connect(db_path)
    cur = db.cursor()

    # 2. Check schema tables
    tables = {name for (name,) in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()}


    expected = {"documents", "pages"}
    missing = expected - tables

    if missing:
        results.append(f"ERROR: Missing tables: {missing}")
    else:
        results.append("OK: All required tables exist.")

    # 3. Count rows
    doc_count = cur.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    page_count = cur.execute("SELECT COUNT(*) FROM pages").fetchone()[0]

    results.append(f"Documents: {doc_count}")
    results.append(f"Pages: {page_count}")

    # 4. Check page files exist
    missing_files = []
    for (path,) in cur.execute("SELECT path FROM pages"):
        if not os.path.exists(path):
            missing_files.append(path)

    if missing_files:
        results.append(f"ERROR: Missing page files ({len(missing_files)}):")
        results.extend("  " + p for p in missing_files[:10])
        if len(missing_files) > 10:
            results.append("  ... (more omitted)")
    else:
        results.append("OK: All page files exist.")

    # 5. Check page_count matches pages in DB
    inconsistent_docs = []

    rows = cur.execute("""
        SELECT d.document_id, d.page_count, COUNT(*)
        FROM documents d
        LEFT JOIN pages p ON p.document_id = d.document_id
        GROUP BY d.document_id
    """).fetchall()

    for doc_id, expected_count, actual_count in rows:
        if expected_count is not None and expected_count != actual_count:
            inconsistent_docs.append((doc_id, expected_count, actual_count))

    if inconsistent_docs:
        results.append("WARNING: Page count mismatches:")
        for doc_id, exp, act in inconsistent_docs[:10]:
            results.append(f"  {doc_id}: expected {exp}, found {act}")
        if len(inconsistent_docs) > 10:
            results.append("  ... (more omitted)")
    else:
        results.append("OK: All documents have consistent page counts.")

    db.close()
    return "\n".join(results)
