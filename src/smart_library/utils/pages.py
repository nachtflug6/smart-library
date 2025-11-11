from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Tuple, Optional, Union

PathLike = Union[str, Path]

def build_pages_index(pages_jsonl: PathLike) -> Dict[Tuple[str, int], str]:
    """
    Return mapping (document_id, page) -> path (string as stored in pages.jsonl).
    """
    idx: Dict[Tuple[str, int], str] = {}
    p = Path(pages_jsonl)
    if not p.exists():
        return idx
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            doc = obj.get("document_id")
            pg = obj.get("page")
            path = obj.get("path")
            if isinstance(doc, str) and isinstance(pg, int) and isinstance(path, str):
                idx[(doc, pg)] = path
    return idx

def resolve_page_path(rel_path: PathLike) -> Optional[Path]:
    """
    Try: as-is, then relative to project root (detect via pyproject.toml/.git), then src/.
    """
    rel = Path(rel_path)
    if rel.exists():
        return rel

    # Detect project root
    here = Path(__file__).resolve()
    for root in [*here.parents]:
        if (root / "pyproject.toml").exists() or (root / ".git").exists():
            cand = root / rel
            if cand.exists():
                return cand
            cand_src = root / "src" / rel
            if cand_src.exists():
                return cand_src
            break
    return None

def read_page_text(rel_path: PathLike) -> Optional[str]:
    p = resolve_page_path(rel_path)
    if not p:
        return None
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return None