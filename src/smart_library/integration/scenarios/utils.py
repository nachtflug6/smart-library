def print_scenario_header(title, goal=None):
	print("""
============================================================
				{title}
============================================================""".format(title=title.upper()))
	if goal:
		print(f"Goal: {goal}\n")

def print_scenario_footer():
	print("============================================================\n")

def print_scenario_table_header(columns):
	col_line = "| " + " | ".join(columns) + " |"
	sep = "|" + "-" * (len(col_line) - 2) + "|"
	print(sep)
	print(col_line)
	print(sep)

def print_scenario_table_row(row):
	print("| " + " | ".join(str(x) for x in row) + " |")
