import sqlite3
import sys
import os
from pathlib import Path
import glob
import site


def _search_for_vec0():
    # 1) try to use installed package's helper if available
    try:
        import sqlite_vec as _sv

        if hasattr(_sv, "loadable_path"):
            try:
                p = _sv.loadable_path()
                if p and Path(p).exists():
                    return str(p)
            except Exception:
                pass
    except Exception:
        pass

    # 2) search site-packages and sys.path for a file/dir named sqlite_vec or vec0
    candidates = []
    search_paths = list(sys.path)
    # include site-packages explicitly
    try:
        search_paths.extend(site.getsitepackages())
    except Exception:
        pass
    try:
        search_paths.append(site.getusersitepackages())
    except Exception:
        pass

    for base in filter(None, dict.fromkeys(search_paths)):
        basep = Path(base)
        if not basep.exists():
            continue
        # check for sqlite_vec package directory
        pkg_dir = basep / "sqlite_vec"
        if pkg_dir.exists():
            # look for vec0 shared lib inside package
            for pattern in ("vec0.*", "*.so", "*.dylib", "*.dll"):
                for p in pkg_dir.glob(pattern):
                    candidates.append(str(p))
        # also search for vec0 files directly under base
        for pattern in ("vec0.*", "sqlite_vec*vec0*", "*vec0*"):
            for p in basep.glob(pattern):
                candidates.append(str(p))

    # 3) common fallback locations
    common = [
        os.path.expanduser("~/.local/lib/python3.11/site-packages/sqlite_vec/vec0"),
        os.path.expanduser("~/.local/lib/python3.10/site-packages/sqlite_vec/vec0"),
    ]
    candidates.extend([c for c in common if c and Path(c).exists()])

    # return first existing candidate
    for c in candidates:
        try:
            if Path(c).exists():
                return c
        except Exception:
            continue

    # final fallback: allow user-specified env var or default path
    return os.getenv("SQLITE_VEC_PATH", "/home/vscode/.local/lib/python3.11/site-packages/sqlite_vec/vec0")


def load_sqlitevec_extension(conn: sqlite3.Connection):
    """Load the sqlite-vec extension into a SQLite connection.

    This function attempts multiple discovery strategies and falls back to
    the `SQLITE_VEC_PATH` environment variable if nothing else is found.
    """
    path = _search_for_vec0()
    conn.enable_load_extension(True)
    conn.load_extension(path)
    conn.enable_load_extension(False)