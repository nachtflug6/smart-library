from lxml import etree
from smart_library.infrastructure.grobid.grobid_models import (
    Header, Author, Affiliation, Facsimile, Surface,
    DocumentBody, Section, Paragraph, InlineRef, Coordinates, CoordinateBox
)
from smart_library.infrastructure.grobid.utils import (
    parse_coords, parse_affiliation, parse_surface, parse_section, parse_author, XMLParser
)

class GrobidMapper:
    NS = {"tei": "http://www.tei-c.org/ns/1.0"}

    # ------------------------------------------------------------
    # MAIN ENTRY: load XML string and extract header + facsimile
    # ------------------------------------------------------------
    def xml_to_struct(self, xml_str: str) -> dict:
        """
        Main entry point.
        Accepts a TEI XML string, extracts the <teiHeader>, <facsimile>, and <body> elements,
        and maps them to dataclasses.
        Returns: {"header": Header, "facsimile": Facsimile, "body": DocumentBody}
        """
        root = etree.fromstring(xml_str.encode("utf-8"))
        parser = XMLParser(root, self.NS)
        header_el = parser.find(".//tei:teiHeader")
        if header_el is None:
            raise ValueError("No <teiHeader> found in XML.")
        facsimile_el = parser.find(".//tei:facsimile")
        body_el = parser.find(".//tei:text/tei:body")

        header = self.parse_tei_header(XMLParser(header_el, self.NS))
        facsimile = self.parse_facsimile(XMLParser(facsimile_el, self.NS)) if facsimile_el is not None else Facsimile()
        body = self.parse_body(XMLParser(body_el, self.NS)) if body_el is not None else DocumentBody()

        return {"header": header, "facsimile": facsimile, "body": body}

    # ------------------------------------------------------------
    # MAPPER: convert <teiHeader> → Header dataclass
    # ------------------------------------------------------------
    def parse_tei_header(self, header_parser: XMLParser) -> Header:
        # TITLE
        title_el = header_parser.find(".//tei:fileDesc/tei:titleStmt/tei:title")
        title = header_parser.text_or_none(title_el)

        # PUBLICATION INFO
        publisher = header_parser.text_or_none(header_parser.find(".//tei:publicationStmt/tei:publisher"))
        
        # Extract date from publicationStmt (primary source)
        pub_date_el = header_parser.find(".//tei:publicationStmt/tei:date")
        published_date = header_parser.get_attr(pub_date_el, "when")
        
        # Extract date from monogr/imprint (fallback source)
        imprint_date_el = header_parser.find(".//tei:sourceDesc//tei:monogr/tei:imprint/tei:date[@type='published']")
        imprint_date = header_parser.get_attr(imprint_date_el, "when")
        
        # Extract submission note text (another fallback)
        submission_note_el = header_parser.find(".//tei:sourceDesc//tei:note[@type='submission']")
        submission_note = header_parser.text_or_none(submission_note_el)

        # IDENTIFIERS (DOI, MD5)
        doi = None
        md5 = None
        for idno in header_parser.findall(".//tei:idno"):
            t = header_parser.get_attr(idno, "type")
            if t == "DOI":
                doi = header_parser.text_or_none(idno)
            elif t == "MD5":
                md5 = header_parser.text_or_none(idno)

        # AFFILIATIONS
        affiliations = {}
        for aff in header_parser.findall(".//tei:analytic/tei:author/tei:affiliation"):
            aff_obj = parse_affiliation(aff, header_parser.ns)
            affiliations[aff_obj.key] = aff_obj

        # AUTHORS
        authors = []
        for author in header_parser.findall(".//tei:analytic/tei:author"):
            author_obj = parse_author(author, header_parser.ns, affiliations)
            if author_obj:
                authors.append(author_obj)

        # KEYWORDS
        keywords = [
            header_parser.text_or_none(term)
            for term in header_parser.findall(".//tei:textClass/tei:keywords/tei:term")
        ]

        # ABSTRACT
        abstract_el = header_parser.find(".//tei:abstract//tei:p")
        abstract = header_parser.itertext(abstract_el) if abstract_el is not None else None

        return Header(
            title=title,
            publisher=publisher,
            published_date=published_date,
            imprint_date=imprint_date,
            submission_note=submission_note,
            doi=doi,
            md5=md5,
            authors=authors,
            affiliations=affiliations,
            keywords=keywords,
            abstract=abstract
        )

    # ------------------------------------------------------------
    # MAPPER: convert <facsimile> → Facsimile dataclass
    # ------------------------------------------------------------
    def parse_facsimile(self, facsimile_parser: XMLParser) -> Facsimile:
        surfaces = [parse_surface(surf) for surf in facsimile_parser.findall("tei:surface")]
        return Facsimile(surfaces=surfaces)

    # ------------------------------------------------------------
    # MAPPER: convert <body> → DocumentBody dataclass
    # ------------------------------------------------------------
    def parse_body(self, body_parser: XMLParser) -> DocumentBody:
        sections = [parse_section(div, body_parser.ns) for div in body_parser.findall(".//tei:div")]
        return DocumentBody(sections=sections)
