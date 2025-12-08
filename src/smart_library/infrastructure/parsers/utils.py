import re
import unicodedata
from dataclasses import dataclass


@dataclass
class NormalizedText:
    content: str


class ContentNormaliser:

    REF_PAT = re.compile(r"\[\s*\d+(?:\s*,\s*\d+)*\s*\]")  # [3, 11]
    FIG_PAT = re.compile(r"Figure\s+\d+")
    TAB_PAT = re.compile(r"Table\s+\d+")

    def normalize(self, text: str) -> NormalizedText:
        # 1. Normalize unicode
        text = unicodedata.normalize("NFKC", text)

        # 2. Remove line breaks inside paragraphs
        #    (GROBID paragraphs have no true line breaks – everything is layout)
        text = text.replace("\n", " ")

        # 3. Normalize hyphenation (most common PDF problem)
        #    Example: "non-sta-\ntionary" or "non-stationary"
        text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)

        # 4. Remove multiple spaces
        text = re.sub(r"\s{2,}", " ", text)

        # 5. Remove reference markers: [3, 11], [7], [15,30]
        text = self.REF_PAT.sub("", text)

        # 6. Remove figure/table mentions if desired
        text = self.FIG_PAT.sub("", text)
        text = self.TAB_PAT.sub("", text)

        # 7. Trim spaces
        text = text.strip()

        return NormalizedText(content=text)


def extract_page_number_from_coords(coords):
    """
    Extracts the first page number from a coords object (with .boxes).
    Returns None if not found.
    """
    if coords and hasattr(coords, "boxes"):
        for box in coords.boxes:
            if hasattr(box, "page"):
                return box.page
    return None
