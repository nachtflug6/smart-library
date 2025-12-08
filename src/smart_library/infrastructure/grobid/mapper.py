from lxml import etree
from smart_library.infrastructure.grobid.models import (
    Header, Author, Affiliation, Facsimile, Surface,
    DocumentBody, Section, Paragraph, InlineRef, Coordinates, CoordinateBox
)
from smart_library.infrastructure.grobid.utils import (
    parse_coords, parse_affiliation, parse_surface, parse_section, parse_author
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
        header_el = root.find(".//tei:teiHeader", self.NS)
        if header_el is None:
            raise ValueError("No <teiHeader> found in XML.")
        facsimile_el = root.find(".//tei:facsimile", self.NS)
        body_el = root.find(".//tei:text/tei:body", self.NS)

        header = self.parse_tei_header(header_el)
        facsimile = self.parse_facsimile(facsimile_el) if facsimile_el is not None else Facsimile()
        body = self.parse_body(body_el) if body_el is not None else DocumentBody()

        return {"header": header, "facsimile": facsimile, "body": body}

    # ------------------------------------------------------------
    # MAPPER: convert <teiHeader> → Header dataclass
    # ------------------------------------------------------------
    def parse_tei_header(self, header) -> Header:
        def text_or_none(el):
            return el.text.strip() if el is not None and el.text else None

        # TITLE
        title_el = header.find(".//tei:fileDesc/tei:titleStmt/tei:title", self.NS)
        title = text_or_none(title_el)

        # PUBLICATION INFO
        publisher = text_or_none(header.find(".//tei:publicationStmt/tei:publisher", self.NS))
        pub_date_el = header.find(".//tei:publicationStmt/tei:date", self.NS)
        published_date = pub_date_el.get("when") if pub_date_el is not None else None

        # IDENTIFIERS (DOI, MD5)
        doi = None
        md5 = None
        for idno in header.findall(".//tei:idno", self.NS):
            t = idno.get("type")
            if t == "DOI":
                doi = text_or_none(idno)
            elif t == "MD5":
                md5 = text_or_none(idno)

        # AFFILIATIONS
        affiliations = {}
        for aff in header.findall(".//tei:analytic/tei:author/tei:affiliation", self.NS):
            aff_obj = parse_affiliation(aff, self.NS)
            affiliations[aff_obj.key] = aff_obj

        # AUTHORS
        authors = []
        for author in header.findall(".//tei:analytic/tei:author", self.NS):
            author_obj = parse_author(author, self.NS, affiliations)
            if author_obj:
                authors.append(author_obj)

        # KEYWORDS
        keywords = [
            text_or_none(term)
            for term in header.findall(".//tei:textClass/tei:keywords/tei:term", self.NS)
        ]

        # ABSTRACT
        abstract_el = header.find(".//tei:abstract//tei:p", self.NS)
        abstract = " ".join(abstract_el.itertext()).strip() if abstract_el is not None else None

        return Header(
            title=title,
            publisher=publisher,
            published_date=published_date,
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
    def parse_facsimile(self, facsimile_el) -> Facsimile:
        surfaces = [parse_surface(surf) for surf in facsimile_el.findall("tei:surface", self.NS)]
        return Facsimile(surfaces=surfaces)

    # ------------------------------------------------------------
    # MAPPER: convert <body> → DocumentBody dataclass
    # ------------------------------------------------------------
    def parse_body(self, body_el) -> DocumentBody:
        sections = [parse_section(div, self.NS) for div in body_el.findall(".//tei:div", self.NS)]
        return DocumentBody(sections=sections)
