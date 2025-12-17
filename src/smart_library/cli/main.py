from typer import Typer
import sys

app = Typer(no_args_is_help=True)

# Import CLI modules to register commands. Use importlib to avoid circular
# import issues when this module is executed as `-m` or imported from
# `smart_library.cli` package.
import importlib
importlib.import_module("smart_library.cli.add")
importlib.import_module("smart_library.cli.delete")
importlib.import_module("smart_library.cli.list")
importlib.import_module("smart_library.cli.show")
importlib.import_module("smart_library.cli.initialize")
importlib.import_module("smart_library.cli.search")

if __name__ == "__main__":
    try:
        app()
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}", file=sys.stderr)
        print("If you need a full traceback, run with the --traceback option.", file=sys.stderr)
        sys.exit(1)