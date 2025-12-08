from lxml import etree
from smart_library.infrastructure.grobid.models import Header, Author, Affiliation

class GrobidMapper:
    NS = {"tei": "http://www.tei-c.org/ns/1.0"}

    # ------------------------------------------------------------
    # MAIN ENTRY: load XML string and extract header
    # ------------------------------------------------------------
    def xml_to_header(self, xml_str: str) -> Header:
        """
        Accepts a TEI XML string, extracts the <teiHeader> element,
        and maps it to a Header dataclass.
        """
        root = etree.fromstring(xml_str.encode("utf-8"))
        header = root.find(".//tei:teiHeader", self.NS)
        if header is None:
            raise ValueError("No <teiHeader> found in XML.")

        return self.parse_tei_header(header)

    # ------------------------------------------------------------
    # MAPPER: convert <teiHeader> → Python dict
    # ------------------------------------------------------------
    def parse_tei_header(self, header) -> Header:
        def text_or_none(el):
            return el.text.strip() if el is not None and el.text else None

        # -------------------------
        # TITLE
        # -------------------------
        title_el = header.find(".//tei:fileDesc/tei:titleStmt/tei:title", self.NS)
        title = text_or_none(title_el)

        # -------------------------
        # PUBLICATION INFO
        # -------------------------
        publisher = text_or_none(header.find(".//tei:publicationStmt/tei:publisher", self.NS))
        pub_date_el = header.find(".//tei:publicationStmt/tei:date", self.NS)
        published_date = pub_date_el.get("when") if pub_date_el is not None else None

        # -------------------------
        # IDENTIFIERS (DOI, MD5)
        # -------------------------
        doi = None
        md5 = None
        for idno in header.findall(".//tei:idno", self.NS):
            t = idno.get("type")
            if t == "DOI":
                doi = text_or_none(idno)
            elif t == "MD5":
                md5 = text_or_none(idno)

        # -------------------------
        # AFFILIATIONS
        # -------------------------
        affiliations = {}
        for aff in header.findall(".//tei:analytic/tei:author/tei:affiliation", self.NS):
            key = aff.get("key")
            inst = text_or_none(aff.find("tei:orgName", self.NS))
            settlement = text_or_none(aff.find("tei:address/tei:settlement", self.NS))
            country = text_or_none(aff.find("tei:address/tei:country", self.NS))
            affiliations[key] = Affiliation(
                key=key,
                institution=inst,
                settlement=settlement,
                country=country
            )

        # -------------------------
        # AUTHORS
        # -------------------------
        authors = []
        for author in header.findall(".//tei:analytic/tei:author", self.NS):
            pers = author.find("tei:persName", self.NS)
            if pers is None:
                continue

            forenames = [fn.text.strip() for fn in pers.findall("tei:forename", self.NS) if fn.text]
            first = forenames[0] if forenames else None
            middle_names = forenames[1:] if len(forenames) > 1 else []
            last = text_or_none(pers.find("tei:surname", self.NS))
            email = text_or_none(author.find("tei:email", self.NS))

            aff_nodes = author.findall("tei:affiliation", self.NS)
            aff_keys = [a.get("key") for a in aff_nodes]

            org_names = []
            for aff in aff_nodes:
                orgs = aff.findall("tei:orgName", self.NS)
                org_names.extend([org.text.strip() for org in orgs if org is not None and org.text])

            # Map affiliation keys to actual Affiliation objects
            author_affiliations = [affiliations[k] for k in aff_keys if k in affiliations]

            authors.append(Author(
                first_name=first,
                middle_names=middle_names,
                last_name=last,
                email=email,
                affiliation_keys=aff_keys,
                org_names=org_names,
                affiliations=author_affiliations
            ))

        # -------------------------
        # KEYWORDS
        # -------------------------
        keywords = [
            text_or_none(term)
            for term in header.findall(".//tei:textClass/tei:keywords/tei:term", self.NS)
        ]

        # -------------------------
        # ABSTRACT
        # -------------------------
        abstract_el = header.find(".//tei:abstract//tei:p", self.NS)
        abstract = " ".join(abstract_el.itertext()).strip() if abstract_el is not None else None

        # -------------------------
        # RESULT DICT
        # -------------------------
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
