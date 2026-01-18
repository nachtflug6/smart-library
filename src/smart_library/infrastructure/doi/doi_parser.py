import re
from typing import Optional


def extract_year_from_doi(doi: str) -> Optional[int]:
    """
    Extract publication year from DOI string when possible.
    
    Handles common patterns:
    - ArXiv: 2501.xxxxx or 10.48550/arXiv.2501.xxxxx (YYMM format)
    - BioRxiv/MedRxiv: 10.1101/2023.12.xxxxx (YYYY.MM pattern)
    - Some publishers: 10.1016/j.2023.xxxxx or 10.1109/2024.xxxxx
    
    Args:
        doi: DOI string to parse
        
    Returns:
        Extracted year as integer, or None if no reliable pattern found
    """
    
    if not doi or not isinstance(doi, str):
        return None
    
    doi = str(doi).strip()
    
    # Strategy 1: ArXiv YYMM pattern (most reliable for preprints)
    # Matches: 2501.xxxxx or arXiv:2501.xxxxx or 10.48550/arXiv.2501.xxxxx
    arxiv_match = re.search(r'(?:arXiv:|/arXiv\.)(\d{4})(?:\.\d+)?', doi, re.IGNORECASE)
    if arxiv_match:
        yymm = arxiv_match.group(1)
        # Convert YYMM to full year (2501 → 2025)
        try:
            yy = int(yymm[:2])
            # Heuristic: 00-30 is 20xx, 31-99 is 19xx
            year = 2000 + yy if yy <= 30 else 1900 + yy
            # Sanity check: year should be reasonable (1900-2100)
            if 1900 <= year <= 2100:
                return year
        except (ValueError, IndexError):
            pass
    
    # Strategy 2: bioRxiv/medRxiv YYYY.MM.xxxxx pattern
    # Matches: 10.1101/2023.12.xxxxx
    biorxiv_match = re.search(r'10\.1101[/.](\d{4})\.(\d{2})', doi)
    if biorxiv_match:
        try:
            year = int(biorxiv_match.group(1))
            if 1900 <= year <= 2100:
                return year
        except ValueError:
            pass
    
    # Strategy 3: Generic YYYY.MM.xxxxx pattern anywhere in DOI
    # Matches: 10.XXXX/2023.12.xxxxx or 10.XXXX/2024.01.xxxxx
    generic_ymd = re.search(r'(\d{4})\.(\d{2})\.', doi)
    if generic_ymd:
        try:
            potential_year = int(generic_ymd.group(1))
            # Only accept if it looks like a valid year (19xx or 20xx)
            if 1900 <= potential_year <= 2100 and potential_year >= 1900:
                return potential_year
        except ValueError:
            pass
    
    # Strategy 4: Publisher-encoded year pattern (journal.YYYY pattern)
    # Matches: 10.1016/j.2023.xxxxx or 10.1109/2024.xxxxx
    # Look for pattern like /j.YYYY or .YYYY/ or similar
    publisher_year = re.search(r'[/.]j\.(\d{4})[/.]', doi)
    if not publisher_year:
        # Try pattern like 10.XXXX/2024.xxxxx (IEEE, Springer, etc)
        publisher_year = re.search(r'10\.\d+[/.](20\d{2})[/.]', doi)
    if publisher_year:
        try:
            potential_year = int(publisher_year.group(1))
            # Be conservative: only accept if looks like a real publication year
            if 1980 <= potential_year <= 2100:
                return potential_year
        except ValueError:
            pass
    
    # No reliable pattern found
    return None
