# src/smart_library/ingest/onboard.py
from __future__ import annotations
import os
import json
import shutil
from pathlib import Path
from typing import Iterable, List, Dict, Set, Optional
from PyPDF2 import PdfReader

INCOMING_DIR = Path("data/pdf/incoming")
CURATED_DIR = Path("data/pdf/curated")
PAGES_DIR = Path("data/pdf/pages")
DOC_JSONL = Path("data/jsonl/entities/documents.jsonl")
PAGES_JSONL = Path("data/jsonl/entities/pages.jsonl")

def _read_jsonl(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]

def _write_jsonl_atomic(path: Path, rows: Iterable[Dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w") as f:
        for obj in rows:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    tmp.replace(path)

def _extract_pages(pdf_path: Path) -> List[Dict]:
    """
    Extract each page's text from the PDF and write to per-page .txt files.
    Returns list of {page: int, path: str}.
    """
    pages_dir = PAGES_DIR / pdf_path.stem
    pages_dir.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(pdf_path))
    records: List[Dict] = []

    for idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        fname = f"p{idx:02d}.txt"
        out_path = pages_dir / fname
        out_path.write_text(text, encoding="utf-8")
        records.append({"page": idx, "path": str(out_path)})

    return records

def onboard_documents() -> List[str]:
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    CURATED_DIR.mkdir(parents=True, exist_ok=True)

    existing_docs = _read_jsonl(DOC_JSONL)
    by_id = {d["document_id"]: d for d in existing_docs}

    changed: List[str] = []

    for pdf in sorted(INCOMING_DIR.glob("*.pdf")):
        doc_id = pdf.stem
        dest = CURATED_DIR / pdf.name
        shutil.move(str(pdf), dest)
        meta = by_id.get(doc_id, {})
        meta.update({
            "document_id": doc_id,
            "title": meta.get("title", ""),
            "venue": meta.get("venue", ""),
            "year": meta.get("year", None),
            "page_count": meta.get("page_count", None),
            "pdf_path": str(dest),
        })
        by_id[doc_id] = meta
        changed.append(doc_id)

    if changed:
        _write_jsonl_atomic(DOC_JSONL, by_id.values())

    return changed

def onboard_pages(document_ids: Optional[Iterable[str]] = None):
    if document_ids is None:
        return
    target_ids: Set[str] = set(document_ids)
    if not target_ids:
        return

    docs = {d["document_id"]: d for d in _read_jsonl(DOC_JSONL)}
    pages_existing = _read_jsonl(PAGES_JSONL)

    # Drop existing JSONL entries for target docs
    retained = [p for p in pages_existing if p.get("document_id") not in target_ids]

    new_pages: List[Dict] = []

    for doc_id in sorted(target_ids):
        doc = docs.get(doc_id)
        if not doc:
            print(f"{doc_id}: skipped (no metadata)")
            continue

        pdf_path = Path(doc["pdf_path"])
        if not pdf_path.exists():
            print(f"{doc_id}: skipped (pdf missing)")
            continue

        # Did we have extracted pages before?
        doc_pages_dir = PAGES_DIR / doc_id
        had_old_files = doc_pages_dir.exists()

        # Clean old extracted pages and re-extract
        if had_old_files:
            shutil.rmtree(doc_pages_dir)

        extracted = _extract_pages(pdf_path)

        for rec in extracted:
            new_pages.append({
                "document_id": doc_id,
                "page": rec["page"],
                "path": rec["path"]
            })

        # Update page_count
        doc["page_count"] = len(extracted)

        # One-liner per document
        print(f"{doc_id}: {'updated' if had_old_files else 'added'}, pages={len(extracted)}")

    # Persist updates
    _write_jsonl_atomic(DOC_JSONL, docs.values())
    combined = retained + sorted(new_pages, key=lambda r: (r["document_id"], r["page"]))
    _write_jsonl_atomic(PAGES_JSONL, combined)

def onboard_all():
    changed = onboard_documents()
    if changed:
        onboard_pages(document_ids=changed)
