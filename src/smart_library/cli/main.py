from typer import Typer
import sys

app = Typer(no_args_is_help=True)

# Import CLI modules to register commands
from .add import add
from .delete import delete
from .list import list
from .show import show
from .initialize import initialize
from .search import search
from .test_sqlitevec import test_sqlitevec

if __name__ == "__main__":
    try:
        app()
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}", file=sys.stderr)
        print("If you need a full traceback, run with the --traceback option.", file=sys.stderr)
        sys.exit(1)