"""Common I/O utilities."""
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timezone


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Read JSONL file into list of dicts."""
    rows: List[Dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


def now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()