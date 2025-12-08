from smart_library.infrastructure.grobid.models import (
    Affiliation, Author, Surface, InlineRef, Paragraph, Section, Coordinates, CoordinateBox
)

def parse_coords(coords_str):
    if not coords_str:
        return None
    boxes = []
    for part in coords_str.split(";"):
        part = part.strip()
        if not part:
            continue
        try:
            nums = list(map(float, part.split(",")))
            if len(nums) >= 5:
                page = int(nums[0])
                x1, y1, x2, y2 = nums[1:5]
                boxes.append(CoordinateBox(page=page, x1=x1, y1=y1, x2=x2, y2=y2))
        except Exception:
            continue
    return Coordinates(boxes=boxes) if boxes else None

def parse_affiliation(aff_el, ns):
    key = aff_el.get("key")
    inst = aff_el.find("tei:orgName", ns)
    settlement = aff_el.find("tei:address/tei:settlement", ns)
    country = aff_el.find("tei:address/tei:country", ns)
    return Affiliation(
        key=key,
        institution=inst.text.strip() if inst is not None and inst.text else None,
        settlement=settlement.text.strip() if settlement is not None and settlement.text else None,
        country=country.text.strip() if country is not None and country.text else None
    )

def parse_surface(surf_el):
    page = int(surf_el.get("n", "0"))
    ulx = float(surf_el.get("ulx", "0.0"))
    uly = float(surf_el.get("uly", "0.0"))
    lrx = float(surf_el.get("lrx", "0.0"))
    lry = float(surf_el.get("lry", "0.0"))
    return Surface(page=page, ulx=ulx, uly=uly, lrx=lrx, lry=lry)

def parse_inline_ref(ref_el, ns):
    ref_type = ref_el.get("type", "")
    target = ref_el.get("target")
    ref_text = "".join(ref_el.itertext()).strip()
    ref_coords = parse_coords(ref_el.get("coords"))
    return InlineRef(
        ref_type=ref_type,
        target=target,
        text=ref_text,
        coords=ref_coords
    )

def parse_paragraph(p_el, ns):
    text = "".join(p_el.itertext()).strip()
    p_coords = parse_coords(p_el.get("coords"))
    references = [parse_inline_ref(ref, ns) for ref in p_el.findall("tei:ref", ns)]
    return Paragraph(
        text=text,
        coords=p_coords,
        references=references
    )

def parse_section(div_el, ns):
    sec_id = div_el.get("n")
    head_el = div_el.find("tei:head", ns)
    title = head_el.text.strip() if head_el is not None and head_el.text else None
    coords = parse_coords(head_el.get("coords")) if head_el is not None else None
    paragraphs = [parse_paragraph(p, ns) for p in div_el.findall("tei:p", ns)]
    return Section(
        id=sec_id,
        title=title,
        coords=coords,
        paragraphs=paragraphs
    )

def parse_author(author_el, ns, affiliations):
    def text_or_none(el):
        return el.text.strip() if el is not None and el.text else None

    pers = author_el.find("tei:persName", ns)
    if pers is None:
        return None

    forenames = [fn.text.strip() for fn in pers.findall("tei:forename", ns) if fn.text]
    first = forenames[0] if forenames else None
    middle_names = forenames[1:] if len(forenames) > 1 else []
    last = text_or_none(pers.find("tei:surname", ns))
    email = text_or_none(author_el.find("tei:email", ns))

    aff_nodes = author_el.findall("tei:affiliation", ns)
    aff_keys = [a.get("key") for a in aff_nodes]

    org_names = []
    for aff in aff_nodes:
        orgs = aff.findall("tei:orgName", ns)
        org_names.extend([org.text.strip() for org in orgs if org is not None and org.text])

    author_affiliations = [affiliations[k] for k in aff_keys if k in affiliations]

    return Author(
        first_name=first,
        middle_names=middle_names,
        last_name=last,
        email=email,
        affiliation_keys=aff_keys,
        org_names=org_names,
        affiliations=author_affiliations
    )