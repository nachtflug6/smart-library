import requests
from pathlib import Path
from smart_library.config import Grobid

class GrobidClient:
    def __init__(
        self,
        fulltext_url: str = Grobid.PROCESSING_TEXT_URL,
        header_url: str = Grobid.PROCESSING_HEADER_URL,
    ):
        self.fulltext_url = fulltext_url
        self.header_url = header_url

    def extract_fulltext(self, pdf_path: Path) -> str:
        """
        Extracts the full text from a PDF document using Grobid.

        Args:
            pdf_path (Path): Path to the PDF file.

        Returns:
            str: Extracted full text in XML format (TEI).
        """
        with open(pdf_path, "rb") as pdf_file:
            files = {"input": pdf_file}
            response = requests.post(self.fulltext_url, files=files)
            response.raise_for_status()
            return response.text

    def extract_header(self, pdf_path: Path) -> str:
        """
        Extracts the header metadata from a PDF document using Grobid.

        Args:
            pdf_path (Path): Path to the PDF file.

        Returns:
            str: Extracted header in XML format (TEI).
        """
        with open(pdf_path, "rb") as pdf_file:
            files = {"input": pdf_file}
            response = requests.post(self.header_url, files=files)
            response.raise_for_status()
            return response.text