import argparse
import importlib
import pkgutil
import sys
import os
import logging


def discover_scenarios():
    """Return a mapping of module_name -> [scenario_fn_names]."""
    scenarios_pkg = "smart_library.integration.scenarios"
    scenarios_path = os.path.dirname(__file__) + "/scenarios"
    sys.path.insert(0, os.path.dirname(__file__))
    results = {}
    for _, module_name, _ in pkgutil.iter_modules([scenarios_path]):
        try:
            mod = importlib.import_module(f"{scenarios_pkg}.{module_name}")
        except Exception:
            continue
        funcs = [a for a in dir(mod) if a.startswith("scenario_") and callable(getattr(mod, a))]
        if funcs:
            results[module_name] = funcs
    return results


def run_scenarios(selected_module=None, selected_func=None):
    """Run discovered scenarios. If selected_module is provided, only that module is used.
    If selected_func is provided, only that function name will be executed (within module).
    """
    scenarios_pkg = "smart_library.integration.scenarios"
    scenarios_path = os.path.dirname(__file__) + "/scenarios"
    sys.path.insert(0, os.path.dirname(__file__))
    from smart_library.integration.context import make_context

    modules = []
    if selected_module:
        modules = [selected_module]
    else:
        modules = [m for m in pkgutil.iter_modules([scenarios_path])]
        modules = [m[1] for m in modules]

    for module_name in modules:
        try:
            mod = importlib.import_module(f"{scenarios_pkg}.{module_name}")
        except Exception as e:
            print(f"[ERROR] importing {module_name}: {e}")
            continue

        for attr in dir(mod):
            if not attr.startswith("scenario_"):
                continue
            if selected_func and attr != selected_func:
                continue

            print(f"\n[RUNNING] {module_name}.{attr}")
            context = make_context()
            try:
                getattr(mod, attr)(context)
            except Exception as e:
                print(f"[ERROR] {module_name}.{attr}: {e}")
            finally:
                context.cleanup()

def _main(argv=None):
    parser = argparse.ArgumentParser(description="Run integration scenarios")
    parser.add_argument("--module", "-m", help="Module name under scenarios/ to run (e.g. grobid_mapping)")
    parser.add_argument("--func", "-f", help="Specific scenario function name to run (e.g. scenario_pdf_to_domain)")
    parser.add_argument("--list", "-l", action="store_true", help="List available scenario modules and functions")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args(argv)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    scenarios = discover_scenarios()
    if args.list:
        for mod, funcs in sorted(scenarios.items()):
            print(mod)
            for f in funcs:
                print(f"  - {f}")
        return


    if args.module and args.module not in scenarios:
        print(f"Module not found: {args.module}")
        return

    run_scenarios(selected_module=args.module, selected_func=args.func)


if __name__ == "__main__":
    _main()
