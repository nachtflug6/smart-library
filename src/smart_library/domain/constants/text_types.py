from enum import Enum

class TextType(str, Enum):
    TITLE = "title"
    ABSTRACT = "abstract"
    SUMMARY = "summary"
    CAPTION = "caption"
    CHUNK = "chunk"
    DESCRIPTION = "description"
    KEYWORD = "keyword"
    HIGHLIGHT = "highlight"
    NOTE = "note"
    PARAPHRASE = "paraphrase"
    EXAMPLE = "example"
