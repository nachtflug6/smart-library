import os
import json
import shutil

DOCS = "data/jsonl/entities/documents.jsonl"
INCOMING = "data/pdf/incoming"
CURATED = "data/pdf/curated"

def migrate_pdfs():
    # Load documents.jsonl
    documents = []
    with open(DOCS, "r", encoding="utf-8") as f:
        for line in f:
            documents.append(json.loads(line))

    if not os.path.exists(CURATED):
        os.makedirs(CURATED)

    moved = 0

    for d in documents:
        doc_id = d["document_id"]

        src = os.path.join(INCOMING, f"{doc_id}.pdf")
        dest = os.path.join(CURATED, f"{doc_id}.pdf")

        if os.path.exists(src):
            print(f"[move] {src} → {dest}")
            shutil.move(src, dest)

            # update json entry
            d["pdf_path"] = dest
            moved += 1
        else:
            print(f"[warn] No PDF found for {doc_id}")

    # write updated jsonl
    with open(DOCS, "w", encoding="utf-8") as f:
        for d in documents:
            f.write(json.dumps(d) + "\n")

    print(f"\n[ok] Migrated {moved} PDFs to curated/ and updated documents.jsonl.")


if __name__ == "__main__":
    migrate_pdfs()


# import os
# import json

# DOCS = "data/jsonl/entities/documents.jsonl"
# INCOMING = "data/pdf/incoming"

# def one_off_add_pdf_paths():
#     # Load current docs
#     documents = []
#     with open(DOCS, "r", encoding="utf-8") as f:
#         for line in f:
#             documents.append(json.loads(line))

#     updated = 0

#     for d in documents:
#         doc_id = d["document_id"]
#         pdf_path_incoming = os.path.join(INCOMING, f"{doc_id}.pdf")

#         if os.path.exists(pdf_path_incoming):
#             d["pdf_path"] = pdf_path_incoming
#             updated += 1
#         else:
#             print(f"[warn] PDF missing for {doc_id}")

#     # Write updated JSONL back
#     with open(DOCS, "w", encoding="utf-8") as f:
#         for d in documents:
#             f.write(json.dumps(d) + "\n")

#     print(f"[ok] Added pdf_path to {updated} documents (pointing to incoming/).")
#     print("Done.")
    

# if __name__ == "__main__":
#     one_off_add_pdf_paths()
