from pathlib import Path
from smart_library.infrastructure.grobid.client import GrobidClient
from smart_library.infrastructure.grobid.mapper import GrobidMapper

class GrobidService:
    def __init__(self, client: GrobidClient = None, mapper: GrobidMapper = None):
        self.client = client or GrobidClient()
        self.mapper = mapper or GrobidMapper()

    def parse_fulltext(self, pdf_path: Path) -> dict:
        """
        Extracts fulltext TEI XML from PDF and parses to structured dataclasses.
        Returns: {"header": Header, "facsimile": Facsimile, "body": DocumentBody}
        """
        xml = self.client.extract_fulltext(pdf_path)
        return self.mapper.xml_to_struct(xml)
