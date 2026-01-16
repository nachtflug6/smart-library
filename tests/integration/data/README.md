# Test Data Directory

This directory contains test data for integration and unit tests.

## Structure

```
tests/integration/data/
├── pdf/              # PDF test files (git-ignored - add your own)
└── db/               # Database test fixtures
```

## PDF Test Files

**Important**: PDF files are not included in this repository due to copyright restrictions.

To run integration tests that require PDFs:

1. **Add your own test PDFs** to `tests/integration/data/pdf/`
   - Use open-source or freely licensed PDFs
   - Update test fixtures accordingly

2. **Example test file structure**:
   ```
   tests/integration/data/pdf/
   ├── sample.pdf           # Your test PDF
   ├── sample.xml           # Extracted metadata (from Grobid)
   └── sample/
       ├── p01.txt          # Page 1 extracted text
       ├── p02.txt          # Page 2 extracted text
       └── ...
   ```

3. **To generate extraction metadata**:
   ```bash
   # Use Grobid to extract PDF structure
   smartlib add path/to/your/pdf.pdf
   ```

## Database Test Fixtures

Test database seeds and fixtures go in `tests/integration/data/db/`.

## Running Tests

```bash
# Unit tests (no PDFs required)
pytest tests/unit/

# Integration tests (requires test PDFs)
pytest tests/integration/

# Run with specific test data
pytest tests/integration/ -k test_name
```

## Using Open-Source PDFs for Testing

**Recommended sources**:
- [arXiv papers](https://arxiv.org/) - Available under CC licenses
- [Project Gutenberg](https://www.gutenberg.org/) - Public domain books
- [Open Access Button](https://www.openaccessbutton.org/) - Free research papers
- [PLOS ONE](https://journals.plos.org/plosone/) - Open access journals

**Steps**:
1. Download a PDF (ensure it's freely licensed)
2. Place in `tests/integration/data/pdf/`
3. Run Grobid extraction
4. Update test fixtures to reference new file

---

**Note**: If you have copyrighted PDFs for testing, keep them in `.gitignore` and document them locally.
