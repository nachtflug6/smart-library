from enum import Enum

class TermType(str, Enum):
    KEYWORD = "keyword"          # Provided by document metadata
    EXTRACTED = "extracted"      # NLP / term extraction
    USER_DEFINED = "user_defined"
    ONTOLOGY = "ontology"        # From controlled vocab / taxonomy