from __future__ import annotations
import json
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Union, Any

PathLike = Union[str, Path]

def read_jsonl(path: PathLike) -> List[dict]:
    p = Path(path)
    if not p.exists():
        return []
    with p.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def iter_jsonl(path: PathLike) -> Iterator[dict]:
    p = Path(path)
    if not p.exists():
        return iter(())
    def _gen() -> Iterator[dict]:
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)
    return _gen()

def write_jsonl(path: PathLike, rows: Iterable[dict], *, mode: str = "w") -> int:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with p.open(mode, encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
        f.flush()
    return count

def append_jsonl(path: PathLike, rows: Iterable[dict]) -> int:
    return write_jsonl(path, rows, mode="a")