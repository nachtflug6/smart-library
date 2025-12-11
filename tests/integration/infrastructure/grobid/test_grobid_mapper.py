import pytest
from pathlib import Path
from smart_library.infrastructure.grobid.client import GrobidClient
from smart_library.infrastructure.grobid.mapper import GrobidMapper


@pytest.mark.integration
@pytest.mark.parametrize("xml_file", [
    "Ma2022.xml",
    "YoonZame2018.xml",
    "TanYe2020.xml",
])
def test_grobid_mapper_xml_to_dict(xml_file):
    xml_path = Path(__file__).parent.parent / "data" / xml_file
    assert xml_path.exists(), f"Test XML not found: {xml_path}"

    with open(xml_path, "r", encoding="utf-8") as f:
        xml_str = f.read()

    mapper = GrobidMapper()
    result = mapper.xml_to_struct(xml_str)

    # assert isinstance(result, dict)
    # assert "metadata" in result
    # assert "text_blocks" in result
    # assert "back_matter" in result
    # # Optionally, check that metadata fields are present
    # for key in ["title", "abstract", "publisher", "publication_date"]:
    #     assert key in result["metadata"]
    print(f"GrobidMapper.xml_to_dict output for {xml_file} (truncated):")
    print(str(result["body"]))  # Print first 500 characters of body for inspection