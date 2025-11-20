from typing import List
import PyPDF2


class PDFReader:
    """Simple text-extraction-based PDF reader."""
    
    def read(self, file_path: str) -> List[str]:
        """
        Extracts text from a PDF file and returns a list of pages.
        
        Returns:
            List[str]: One string per PDF page. Empty pages become "".
        Raises:
            FileNotFoundError: if the file does not exist.
            ValueError: if PDF is unreadable.
        """
        try:
            pages = []
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text() or ""
                    pages.append(text)
            return pages

        except FileNotFoundError:
            raise

        except Exception as e:
            raise ValueError(f"Failed to read PDF: {file_path}") from e
