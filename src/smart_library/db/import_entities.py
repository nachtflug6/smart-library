import sqlite3
import json

def import_documents():
    db = sqlite3.connect("db/smart_library.db")
    cur = db.cursor()

    with open("data/jsonl/entities/documents.jsonl") as f:
        for line in f:
            p = json.loads(line)

            cur.execute("""
                INSERT OR REPLACE INTO documents (
                    document_id,
                    title,
                    venue,
                    year,
                    page_count,
                    pdf_path
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                p["document_id"],
                p["title"],
                p.get("venue"),
                p.get("year"),
                p.get("page_count"),
                p.get("pdf_path")
            ))

    db.commit()
    db.close()
    print("Imported documents.")

def import_pages():
    db = sqlite3.connect("db/smart_library.db")
    cur = db.cursor()

    with open("data/jsonl/entities/pages.jsonl") as f:
        for line in f:
            p = json.loads(line)
            cur.execute(
                """
                INSERT OR REPLACE INTO pages(document_id, page, path)
                VALUES (?, ?, ?)
                """,
                (
                    p["document_id"], 
                    p["page"], 
                    p["path"])
            )

    db.commit()
    db.close()
    print("Imported pages.")


if __name__ == "__main__":
    import_pages()