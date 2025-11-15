"""PDF extraction utilities."""
from __future__ import annotations
from pathlib import Path
from typing import List, Dict
from PyPDF2 import PdfReader


def extract_pages_to_text(pdf_path: Path, output_dir: Path) -> List[Dict]:
    """
    Extract each page's text from a PDF and write to per-page .txt files.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory where page text files will be saved
        
    Returns:
        List of dicts with {page: int, path: str} for each extracted page
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(pdf_path))
    records: List[Dict] = []

    for idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        fname = f"p{idx:02d}.txt"
        out_path = output_dir / fname
        out_path.write_text(text, encoding="utf-8")
        records.append({"page": idx, "path": str(out_path)})

    return records