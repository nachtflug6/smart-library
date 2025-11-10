import json
from pathlib import Path
from thefuzz import fuzz

TERMS_RAW_PATH = Path("data/jsonl/joins/terms_raw.jsonl")
TERMS_PAGES_RAW_PATH = Path("data/jsonl/joins/terms_pages_raw.jsonl")
TERMS_PAGES_VERIFIED_PATH = Path("data/jsonl/joins/terms_pages_verified.jsonl")
TERMS_VERIFIED_PATH = Path("data/jsonl/joins/terms_verified.jsonl")
PAGES_PATH = Path("data/jsonl/entities/pages.jsonl")

def verify_string_in_string(term, text, tolerance=90):
    """Check if the term exists in the text using fuzzy matching."""
    # Use partial_ratio for substring matching with fuzzy tolerance
    return fuzz.partial_ratio(term.lower(), text.lower()) >= tolerance

def load_page_text(file_path):
    """Load the text from the specified file path."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def clear_verified_files():
    """Clear the contents of the verified JSONL files."""
    for path in [TERMS_PAGES_VERIFIED_PATH, TERMS_VERIFIED_PATH]:
        with open(path, 'w') as f:
            pass  # Clear the file

def verify_term_occurrences(tolerance=80):
    """
    Verify term occurrences using fuzzy matching.
    
    Args:
        tolerance: Fuzzy matching threshold (0-100). Default 80.
                  Higher = stricter matching, lower = more lenient.
    """
    clear_verified_files()  # Clear verified files before running

    verified_terms_dict = {}  # term -> metadata from terms_raw.jsonl
    verified_pages = []  # List of verified page entries

    # Load terms from terms_raw.jsonl (for metadata lookup)
    terms_raw_dict = {}
    with open(TERMS_RAW_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            term_entry = json.loads(line)
            terms_raw_dict[term_entry['term']] = term_entry

    # Load pages from pages.jsonl (for path lookup)
    pages = {}
    with open(PAGES_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line)
            page_key = f"{entry['document_id']}_{entry['page']}"
            pages[page_key] = entry['path']

    # Process each entry in terms_pages_raw.jsonl
    with open(TERMS_PAGES_RAW_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            page_entry = json.loads(line)
            term = page_entry['term']
            document_id = page_entry['document_id']
            page_number = page_entry['page']
            page_key = f"{document_id}_{page_number}"

            # Check if we can verify this term on this page
            if page_key in pages:
                source_page_path = Path(pages[page_key])
                
                # Skip if page file doesn't exist
                if not source_page_path.exists():
                    continue
                
                try:
                    source_page_text = load_page_text(source_page_path)

                    # Verify term exists in page text using fuzzy matching
                    if verify_string_in_string(term, source_page_text, tolerance=tolerance):
                        # Add this verified page entry (exact copy from terms_pages_raw)
                        verified_pages.append(page_entry)
                        
                        # Track term for terms_verified (only once per term)
                        if term not in verified_terms_dict and term in terms_raw_dict:
                            verified_terms_dict[term] = terms_raw_dict[term]
                            
                except Exception as e:
                    # Skip if file cannot be read
                    continue

    # Write verified page entries to terms_pages_verified.jsonl
    # (multiple entries per term, one per verified document-page)
    with open(TERMS_PAGES_VERIFIED_PATH, 'w', encoding='utf-8') as f:
        for entry in verified_pages:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    # Write unique verified terms to terms_verified.jsonl
    # (one entry per term, only if at least one page was verified)
    with open(TERMS_VERIFIED_PATH, 'w', encoding='utf-8') as f:
        for term in sorted(verified_terms_dict.keys()):
            f.write(json.dumps(verified_terms_dict[term], ensure_ascii=False) + '\n')

    print(f"Verified {len(verified_terms_dict)} unique terms (tolerance={tolerance})")
    print(f"Verified {len(verified_pages)} term-page associations")

# Call the verification function
if __name__ == "__main__":
    verify_term_occurrences(tolerance=80)