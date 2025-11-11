from smart_library.utils.jsonl import read_jsonl, write_jsonl
from smart_library.utils.pages import build_pages_index, read_page_text
from smart_library.utils.textnorm import normalize_term, normalize_text_window

# Replace local JSONL/text helpers with imports above
# Use read_jsonl/write_jsonl for I/O and read_page_text for page content