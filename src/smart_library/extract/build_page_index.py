import json
from pathlib import Path

def build_page_index():
    root = Path("data/pdf/pages")
    out = Path("data/jsonl/entities/pages.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", encoding="utf-8") as f:
        for paper_dir in root.iterdir():
            if not paper_dir.is_dir():
                continue

            paper_id = paper_dir.name
            pages = sorted(paper_dir.glob("p*.txt"))

            for p in pages:
                page_num = int(p.stem[1:])  # p01 -> 1
                rec = {
                    "paper_id": paper_id,
                    "page": page_num,
                    "path": str(p)
                }
                f.write(json.dumps(rec) + "\n")

    print("[ok] generated pages.jsonl")

if __name__ == "__main__":
    build_page_index()