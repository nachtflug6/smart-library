from tabulate import tabulate


def print_scenario_header(title, goal=None):
	print("""
============================================================
				{title}
============================================================""".format(title=title.upper()))
	if goal:
		print(f"Goal: {goal}\n")


_current_table_columns = None
_current_table_rows = []


def _flush_table():
	global _current_table_columns, _current_table_rows
	if _current_table_columns and _current_table_rows:
		print(tabulate(_current_table_rows, headers=_current_table_columns, tablefmt="grid"))
		# Clear buffered rows after printing so repeated flushes don't reprint the same table
		_current_table_rows = []


def print_scenario_footer():
	global _current_table_columns, _current_table_rows
	# Flush any remaining table and reset state
	_flush_table()
	print("============================================================\n")
	_current_table_columns = None
	_current_table_rows = []


def print_scenario_table_header(columns):
	global _current_table_columns, _current_table_rows
	# If previous table exists, flush it before starting a new one
	if _current_table_columns and _current_table_rows:
		_flush_table()
	_current_table_columns = columns
	_current_table_rows = []


def print_scenario_table_row(row):
	global _current_table_columns, _current_table_rows
	if not _current_table_columns:
		# Fallback to simple print if no header defined
		print(" | ".join(str(x) for x in row))
		return
	# Buffer the row; don't reprint the entire table each time.
	_current_table_rows.append(row)


try:
    from smart_library.utils.print import print_search_results_boxed as _boxed_printer
except Exception:
    _boxed_printer = None


def print_search_results_boxed(results, text_service, doc_service=None, entity_service=None, max_chars=None):
    """Thin wrapper to the general `utils.print.print_search_results_boxed`.

    Falls back to a compact listing if the general printer isn't available.
    """
    if _boxed_printer:
        return _boxed_printer(results, text_service, doc_service=doc_service, entity_service=entity_service, max_chars=max_chars)

    # Fallback simple print
    for r in results or []:
        tid = r.get("id") if isinstance(r, dict) else getattr(r, "id", None)
        score = (r.get("cosine_similarity") or r.get("cosine")) if isinstance(r, dict) else getattr(r, "cosine_similarity", None) or getattr(r, "cosine", 0.0)
        print(f"{tid} | score={float(score or 0.0):.4f}")
