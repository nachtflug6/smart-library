# src/smart_library/ingest/onboard.py
from __future__ import annotations
import shutil
from pathlib import Path
from typing import Iterable, List, Dict, Set, Optional

from smart_library.config import DOC_PDF_DIR, DOC_TEXT_DIR, ENTITIES_JSONL
from smart_library.utils.jsonl import read_jsonl, write_jsonl
from smart_library.utils.pdf import extract_pages_to_text


def onboard_document(pdf_path: Path | str, *, label: Optional[str] = None) -> str:
    """
    Onboard a single PDF document:
    - Copy to curated PDF directory
    - Create/update document entity in entities.jsonl
    - Extract pages and create page entities
    
    Args:
        pdf_path: Path to PDF file to onboard
        label: Optional human-readable label for the document
        
    Returns:
        document_id (e.g., "doc:stem")
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if not pdf_path.suffix.lower() == ".pdf":
        raise ValueError(f"Not a PDF file: {pdf_path}")
    
    DOC_PDF_DIR.mkdir(parents=True, exist_ok=True)
    DOC_TEXT_DIR.mkdir(parents=True, exist_ok=True)
    
    stem = pdf_path.stem
    doc_id = f"doc:{stem}"
    dest = DOC_PDF_DIR / pdf_path.name
    
    # Copy PDF to curated location
    shutil.copy2(str(pdf_path), dest)
    
    # Load existing entities
    existing_entities = read_jsonl(ENTITIES_JSONL)
    by_id = {e["id"]: e for e in existing_entities if e.get("id")}
    
    # Create/update document entity
    prev = by_id.get(doc_id)
    prev_label = prev.get("label") if prev else None
    doc_entity = {
        "id": doc_id,
        "type": "document",
        "label": label or prev_label or stem,
        "data": {
            "pdf_path": str(dest),
        }
    }
    
    # Preserve existing data fields if present
    if prev and "data" in prev:
        doc_entity["data"].update(prev["data"])
        doc_entity["data"]["pdf_path"] = str(dest)  # Always update path
    
    by_id[doc_id] = doc_entity
    
    # Persist document entity
    write_jsonl(ENTITIES_JSONL, by_id.values())
    
    # Extract and persist pages
    onboard_pages(document_ids=[stem])
    
    return doc_id


def _to_stem(value: str) -> str:
    """Normalize 'doc:STEM' or 'STEM' to STEM."""
    return value[4:] if value.startswith("doc:") else value


def onboard_pages(document_ids: Optional[Iterable[str]] = None):
    """
    Extract pages for specified documents (accepts stems or 'doc:' IDs).
    Pass e.g., ['ZhangZheng2023'] or ['doc:ZhangZheng2023'].
    """
    if document_ids is None:
        return
    target_stems: Set[str] = { _to_stem(s) for s in document_ids }
    if not target_stems:
        return

    # Load all entities
    entities = read_jsonl(ENTITIES_JSONL)
    by_id = {e["id"]: e for e in entities if e.get("id")}

    # Find document entities for target stems
    docs: Dict[str, Dict] = {}
    for stem in target_stems:
        doc_id = f"doc:{stem}"
        if doc_id in by_id:
            docs[stem] = by_id[doc_id]

    # Remove existing page entities for target documents
    retained = [e for e in entities if not (
        e.get("type") == "page" and
        _to_stem(e.get("data", {}).get("document_id", "")) in target_stems
    )]
    by_id = {e["id"]: e for e in retained}

    for stem in sorted(target_stems):
        doc_entity = docs.get(stem)
        if not doc_entity:
            print(f"{stem}: skipped (no document entity)")
            continue

        pdf_path = Path(doc_entity["data"]["pdf_path"])
        if not pdf_path.exists():
            print(f"{stem}: skipped (pdf missing)")
            continue

        # Clean old extracted pages and re-extract
        doc_pages_dir = DOC_TEXT_DIR / stem
        had_old_files = doc_pages_dir.exists()
        if had_old_files:
            shutil.rmtree(doc_pages_dir)

        extracted = extract_pages_to_text(pdf_path, doc_pages_dir)

        for rec in extracted:
            page_num = rec["page"]
            page_id = f"page:{stem}:{page_num:02d}"
            page_entity = {
                "id": page_id,
                "type": "page",
                "label": f"{stem} p{page_num:02d}",
                "data": {
                    "document_id": f"doc:{stem}",
                    "page": page_num,
                    "text_path": rec["path"],
                }
            }
            by_id[page_id] = page_entity

        # Update page_count in document entity
        doc_entity["data"]["page_count"] = len(extracted)
        by_id[f"doc:{stem}"] = doc_entity

        print(f"{stem}: {'updated' if had_old_files else 'added'}, pages={len(extracted)}")

    # Persist all entities
    write_jsonl(ENTITIES_JSONL, by_id.values())


def onboard_documents(pdf_paths: Iterable[Path | str]) -> List[str]:
    """Onboard multiple PDF documents."""
    onboarded: List[str] = []
    for pdf_path in pdf_paths:
        try:
            doc_id = onboard_document(pdf_path)
            onboarded.append(doc_id)
        except (FileNotFoundError, ValueError) as e:
            print(f"Skipping {pdf_path}: {e}")
    return onboarded
