
from pathlib import Path
from smart_library.infrastructure.grobid.service import GrobidService
from smart_library.infrastructure.parsers.document import parse_document
from smart_library.utils.print import print_document
from .utils import print_scenario_header, print_scenario_footer
from smart_library.config import DATA_DIR

def scenario_grobid_extraction(context=None, pdf_path=None, verbose=False):
	"""
	Scenario: Extracts and parses a PDF using Grobid, returning the Document object.
	Args:
		context: Optional context object (unused).
		pdf_path (str or Path): Path to the PDF file. Defaults to Ma2022.pdf in data_dev.
		verbose (bool): If True, prints document summary.
	Returns:
		Document: Parsed document object.
	"""
	if pdf_path is None:
		pdf_path = DATA_DIR / "db" / "pdf" / "pdf" / "Ma2022.pdf"
	else:
		pdf_path = Path(pdf_path)
	assert pdf_path.exists(), f"PDF not found: {pdf_path}"

	service = GrobidService()
	grobid_struct = service.parse_fulltext(pdf_path)
	doc = parse_document(grobid_struct, source_path=str(pdf_path))

	if verbose:
		print_scenario_header("Grobid Extraction", goal=f"Extract and parse PDF using Grobid.\n\nPDF: {pdf_path}")
		print_document(doc)
		print_scenario_footer()

	return doc
