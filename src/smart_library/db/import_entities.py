import sqlite3
import json

def import_pages():
    db = sqlite3.connect("db/smart_library.db")
    cur = db.cursor()

    with open("data/jsonl/joins/pages.jsonl") as f:
        for line in f:
            p = json.loads(line)
            cur.execute(
                """
                INSERT OR REPLACE INTO pages(paper_id, page, path)
                VALUES (?, ?, ?)
                """,
                (p["paper_id"], p["page"], p["path"])
            )

    db.commit()
    db.close()

if __name__ == "__main__":
    import_pages()