from enum import Enum

class DocumentType(str, Enum):
    RESEARCH_ARTICLE = "research_article"
    BOOK = "book"
    THESIS = "thesis"
    WEBPAGE = "webpage"
    REPORT = "report"
    SLIDES = "slides"
    BLOG_POST = "blog_post"
    TECH_DOC = "technical_documentation"