import importlib
import pkgutil
import sys
import os

def run_all_scenarios():
    """
    Dynamically discover and run all scenario_* functions in scenarios/ directory.
    """
    scenarios_pkg = "smart_library.integration.scenarios"
    scenarios_path = os.path.dirname(__file__) + "/scenarios"
    sys.path.insert(0, os.path.dirname(__file__))
    from smart_library.integration.context import make_context
    for _, module_name, _ in pkgutil.iter_modules([scenarios_path]):
        mod = importlib.import_module(f"{scenarios_pkg}.{module_name}")
        for attr in dir(mod):
            if attr.startswith("scenario_") and callable(getattr(mod, attr)):
                print(f"\n[RUNNING] {module_name}.{attr}")
                context = make_context()  # Create a new context (and DB) for each scenario
                try:
                    getattr(mod, attr)(context)
                except Exception as e:
                    print(f"[ERROR] {module_name}.{attr}: {e}")
                finally:
                    context.cleanup()

if __name__ == "__main__":
    run_all_scenarios()
