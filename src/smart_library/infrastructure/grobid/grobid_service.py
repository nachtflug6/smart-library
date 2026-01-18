from pathlib import Path
from smart_library.infrastructure.grobid.grobid_client import GrobidClient
from smart_library.infrastructure.grobid.grobid_mapper import GrobidMapper

class GrobidService:
    def __init__(self, client: GrobidClient = None, mapper: GrobidMapper = None):
        self.client = client or GrobidClient()
        self.mapper = mapper or GrobidMapper()

    def extract_fulltext(self, pdf_path: Path) -> dict:
        """
        Extracts fulltext TEI XML from PDF and parses to structured dataclasses.
        Returns: {"header": Header, "facsimile": Facsimile, "body": DocumentBody}
        """
        xml = self.client.extract_fulltext(pdf_path)
        return self.mapper.xml_to_struct(xml)
    
    def extract_fulltext_with_xml(self, pdf_path: Path) -> tuple[dict, str]:
        """
        Extracts fulltext TEI XML from PDF and parses to structured dataclasses.
        Also returns the raw XML string for buffering/saving.
        
        Returns: (struct_dict, xml_string) where struct_dict contains:
                 {"header": Header, "facsimile": Facsimile, "body": DocumentBody}
                 and xml_string is the raw TEI XML from Grobid.
        """
        xml = self.client.extract_fulltext(pdf_path)
        struct = self.mapper.xml_to_struct(xml)
        return struct, xml
    
    @staticmethod
    def save_xml(doc_id: str, xml_content: str) -> Path:
        """
        Save raw Grobid XML output to disk.
        
        Args:
            doc_id: Document ID to use as filename
            xml_content: Raw XML string from Grobid
            
        Returns:
            Path to saved XML file
        """
        from smart_library.config import DOC_XML_DIR
        
        # Ensure directory exists
        DOC_XML_DIR.mkdir(parents=True, exist_ok=True)
        
        xml_path = DOC_XML_DIR / f"{doc_id}.xml"
        xml_path.write_text(xml_content, encoding="utf-8")
        return xml_path
