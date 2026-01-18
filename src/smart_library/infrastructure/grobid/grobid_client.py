import requests
from pathlib import Path
from smart_library.config import Grobid
import logging

logger = logging.getLogger(__name__)

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
        
        Attempts consolidation with external services (CrossRef) first,
        falls back to local-only extraction if network/service issues occur.

        Args:
            pdf_path (Path): Path to the PDF file.

        Returns:
            str: Extracted full text in XML format (TEI).
        """
        with open(pdf_path, "rb") as pdf_file:
            files = {"input": pdf_file}
            
            # Try with consolidation first
            try:
                response = requests.post(
                    self.fulltext_url, 
                    files=files, 
                    data=[
                        ("generateCoordinates", "1"),
                        ("teiCoordinates", "p"),
                        ("teiCoordinates", "head"),
                        ("teiCoordinates", "div"),
                        ("consolidateHeader", "1"),
                    ],
                    timeout=30
                )
                response.raise_for_status()
                return response.text
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.warning(f"Consolidation failed ({e.__class__.__name__}), retrying without consolidation")
                # Fallback: retry without consolidation
                pdf_file.seek(0)  # Reset file pointer
                response = requests.post(
                    self.fulltext_url, 
                    files={"input": pdf_file}, 
                    data=[
                        ("generateCoordinates", "1"),
                        ("teiCoordinates", "p"),
                        ("teiCoordinates", "head"),
                        ("teiCoordinates", "div"),
                    ],
                    timeout=30
                )
                response.raise_for_status()
                return response.text

    def extract_header(self, pdf_path: Path) -> str:
        """
        Extracts the header metadata from a PDF document using Grobid.
        
        Attempts consolidation with external services (CrossRef) first,
        falls back to local-only extraction if network/service issues occur.

        Args:
            pdf_path (Path): Path to the PDF file.

        Returns:
            str: Extracted header in XML format (TEI).
        """
        with open(pdf_path, "rb") as pdf_file:
            files = {"input": pdf_file}
            
            # Try with consolidation first
            try:
                response = requests.post(
                    self.header_url, 
                    files=files, 
                    data=[("consolidateHeader", "1")],
                    timeout=30
                )
                response.raise_for_status()
                return response.text
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.warning(f"Consolidation failed ({e.__class__.__name__}), retrying without consolidation")
                # Fallback: retry without consolidation
                pdf_file.seek(0)  # Reset file pointer
                response = requests.post(
                    self.header_url, 
                    files={"input": pdf_file},
                    timeout=30
                )
                response.raise_for_status()
                return response.text
