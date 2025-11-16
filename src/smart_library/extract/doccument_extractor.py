class DocumentMetadataExtractor:
    def __init__(self, extractor: BaseExtractor):
        self.extractor = extractor

    def extract(self, document: Document):
        # 1. select pages
        first_page = document.pages[0].text
        
        # 2. normalize text (optional)
        text = self.normalize(first_page)

        # 3. build prompts
        system_prompt = self.system_prompt()
        user_prompt = self.user_prompt()

        # 4. call base extractor
        raw = self.extractor.extract_one(
            text=text,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            verify=True
        )

        # 5. postprocess/amalgamate
        return self.amalgamate(raw)

    def normalize(self, text: str) -> str:
        return text.strip()

    def system_prompt(self) -> str:
        return "You are a precise metadata extractor..."

    def user_prompt(self) -> str:
        return """Extract metadata..."""

    def amalgamate(self, raw):
        # optional
        return raw