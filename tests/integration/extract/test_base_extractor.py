"""Integration tests for BaseExtractor with verification logic."""

import pytest
import json

from smart_library.extract.extractor import BaseExtractor
from smart_library.llm.openai_client import OpenAIClient


@pytest.fixture
def openai_client():
    """Create OpenAI client (requires OPENAI_API_KEY env var)."""
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")
    return OpenAIClient(api_key=api_key, default_model="gpt-4o-mini", validate_key=False)


@pytest.fixture
def academic_paper_text():
    """Academic paper excerpt."""
    return """
    Neural Attention Mechanisms in Deep Learning
    
    Authors: Sarah Chen, Michael Rodriguez, Wei Zhang
    Stanford University, Department of Computer Science
    sarah.chen@stanford.edu
    
    Abstract: We study attention mechanisms in neural networks including 
    self-attention and multi-head attention. Results on ImageNet and SQuAD datasets.
    
    Keywords: attention mechanisms, transformers, deep learning
    
    Conference: NeurIPS 2023
    DOI: 10.1234/neurips.2023.12345
    """


@pytest.fixture
def extractor(openai_client):
    """Create BaseExtractor with logging."""
    class LoggingExtractor(BaseExtractor):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.last_raw_output = None
            self.last_verified_output = None
        
        def extract_one(self, text: str, **kwargs):
            verify = kwargs.get('verify', True)
            
            kwargs_no_verify = kwargs.copy()
            kwargs_no_verify['verify'] = False
            self.last_raw_output = super().extract_one(text, **kwargs_no_verify)
            
            if verify:
                self.last_verified_output = super().extract_one(text, **kwargs)
                return self.last_verified_output
            else:
                self.last_verified_output = None
                return self.last_raw_output
    
    return LoggingExtractor(
        openai_client,
        model="gpt-4o-mini",
        temperature=0.0,
        enforce_json=True,
    )


def log_comparison(name: str, text: str, system_prompt: str, user_prompt: str, raw: dict, verified: dict = None):
    """Log prompts, text, and raw vs verified output."""
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"{'='*80}")
    
    print(f"\nSOURCE TEXT:")
    print(f"{text[:300]}..." if len(text) > 300 else text)
    
    print(f"\nSYSTEM PROMPT:")
    print(system_prompt)
    
    print(f"\nUSER PROMPT:")
    print(user_prompt)
    
    print(f"\nRAW LLM OUTPUT (before verification):")
    print(json.dumps(raw, indent=2))
    
    if verified is not None:
        print(f"\nVERIFIED OUTPUT (after verification):")
        print(json.dumps(verified, indent=2))
        if isinstance(raw, dict) and isinstance(verified, dict):
            changes = []
            for k in raw.keys():
                if raw.get(k) != verified.get(k):
                    changes.append(f"  ✗ {k}: {raw[k]} → {verified[k]}")
            if changes:
                print("\nCHANGES MADE BY VERIFICATION:")
                print("\n".join(changes))
            else:
                print("\nCHANGES MADE BY VERIFICATION:")
                print("  ✓ No changes - all values verified successfully")
    print(f"{'='*80}\n")


def _with_text(user_prompt: str, text: str) -> str:
    """Embed source text into the user prompt (prompts are strings only)."""
    return f"{user_prompt.rstrip()}\n\nSOURCE TEXT:\n{text.strip()}"


def test_valid_extraction(extractor, academic_paper_text):
    """Test extracting data that exists in text."""
    system_prompt = """You are an information extraction assistant.
    - Return valid JSON only.
    - Extract text verbatim.
    - If the text for a field appears anywhere in the document, you MUST extract it.
    - Only return null when the field truly does not exist in the text.
    - Never guess or infer values.
    """

    user_prompt = """Extract the following fields from the following document text as JSON.

    Field descriptions:
    - title: the title or heading of the document.
    - authors: list of authors mentioned by name.
    - institution: the university, organization, or affiliation stated.
    - email: any email address present in the text.

    Expected JSON format:
    {
    "title": "string | null",
    "authors": ["string"] | null,
    "institution": "string | null",
    "email": "string | null"
    }
"""
    composed_user = _with_text(user_prompt, academic_paper_text)
    
    result = extractor.extract_one(
        academic_paper_text,
        system_prompt=system_prompt,
        user_prompt=composed_user,
        verify=True,
        token_threshold=0.5,
    )
    
    log_comparison(
        "Valid Extraction",
        academic_paper_text,
        system_prompt,
        composed_user,
        extractor.last_raw_output,
        extractor.last_verified_output
    )
    
    # Should extract real values
    assert result.get("title") is not None
    assert result.get("authors") is not None
    assert isinstance(result.get("authors"), list)


def test_hallucination_nullified(extractor, academic_paper_text):
    """Test that hallucinated values get nullified."""
    system_prompt = """You are an accurate information extraction assistant.
- Return valid JSON only. 
- Extract text verbatim
- If a field appears anywhere in the text, you MUST extract it."""

    user_prompt = """Extract the following fields from the text as JSON.

Field descriptions:
- title: the title or heading of the document.
- authors: list of authors mentioned by name.
- institution: the university, organization, or affiliation stated.
- email: any email address present in the text.

Expected JSON format:
{
  "title": "string | null",
  "authors": ["string"] | null,
  "institution": "string | null",
  "email": "string | null"
}

"""
    composed_user = _with_text(user_prompt, academic_paper_text)
    
    result = extractor.extract_one(
        academic_paper_text,
        system_prompt=system_prompt,
        user_prompt=composed_user,
        verify=True,
        token_threshold=0.5,
    )
    
    log_comparison(
        "Hallucination Test",
        academic_paper_text,
        system_prompt,
        composed_user,
        extractor.last_raw_output,
        extractor.last_verified_output
    )
    
    # Real fields should exist
    assert result.get("title") is not None
    
    # Fake fields should be None (LLM should return null, or verification catches it)
    assert result.get("isbn") is None
    assert result.get("price") is None


def test_verification_disabled(extractor, academic_paper_text):
    """Test that with verify=False, no nullification happens."""
    system_prompt = """You are a precise information extraction assistant.
- Return ONLY valid JSON
- Extract ONLY information explicitly present in the source text
- Do NOT invent, guess, or hallucinate any information
- If information is not present, use null"""

    user_prompt = """Extract the following fields from the text:

Expected JSON format:
{
  "title": "string | null",
  "fake_field_xyz": "string | null"
}

Extract only information present in the text. Use null for missing fields."""
    composed_user = _with_text(user_prompt, academic_paper_text)
    
    result = extractor.extract_one(
        academic_paper_text,
        system_prompt=system_prompt,
        user_prompt=composed_user,
        verify=False,
    )
    
    log_comparison(
        "Verification Disabled",
        academic_paper_text,
        system_prompt,
        composed_user,
        result
    )
    
    # Without verification, LLM output is kept as-is
    assert "error" not in result


def test_token_threshold_strict(extractor, academic_paper_text):
    """Test strict threshold filters partial matches."""
    system_prompt = """You are a precise information extraction assistant.
- Return ONLY valid JSON
- Extract ONLY information explicitly present in the source text
- Do NOT invent, guess, or hallucinate any information
- If information is not present, use null"""

    user_prompt = """Extract the following fields from the text:

Expected JSON format:
{
  "authors": ["string"] | null,
  "conference": "string | null"
}

Extract only information present in the text. Use null for missing fields."""
    composed_user = _with_text(user_prompt, academic_paper_text)
    
    strict = extractor.extract_one(
        academic_paper_text,
        system_prompt=system_prompt,
        user_prompt=composed_user,
        verify=True,
        token_threshold=0.9,
    )
    
    lenient = extractor.extract_one(
        academic_paper_text,
        system_prompt=system_prompt,
        user_prompt=composed_user,
        verify=True,
        token_threshold=0.3,
    )
    
    print(f"\n{'='*80}")
    print("TOKEN THRESHOLD COMPARISON")
    print(f"{'='*80}")
    print(f"\nSOURCE TEXT:")
    print(f"{academic_paper_text[:300]}...")
    print(f"\nSYSTEM PROMPT:")
    print(system_prompt)
    print(f"\nUSER PROMPT:")
    print(composed_user)
    print(f"\nSTRICT (threshold=0.9):")
    print(json.dumps(strict, indent=2))
    print(f"\nLENIENT (threshold=0.3):")
    print(json.dumps(lenient, indent=2))
    print(f"{'='*80}\n")


def test_technical_terms_valid(extractor):
    """Test extracting technical terms present in text."""
    text = """
    We use transformers with self-attention and cross-attention mechanisms.
    The model employs multi-head attention with 8 heads.
    Training uses backpropagation and gradient descent optimization.
    """
    
    system_prompt = """You are a precise information extraction assistant.
- Return ONLY valid JSON
- Extract ONLY information explicitly present in the source text
- Do NOT invent, guess, or hallucinate any information
- If information is not present, use null"""

    user_prompt = """Extract technical terms from the text.

Expected JSON format:
{
  "terms": ["string"] | null
}

List all AI/ML technical terms explicitly mentioned in the text. Use null if none found."""
    composed_user = _with_text(user_prompt, text)
    
    result = extractor.extract_one(
        text,
        system_prompt=system_prompt,
        user_prompt=composed_user,
        verify=True,
        token_threshold=0.5,
    )
    
    log_comparison(
        "Technical Terms - Valid",
        text,
        system_prompt,
        composed_user,
        extractor.last_raw_output,
        extractor.last_verified_output
    )
    
    # Should extract real terms
    if result.get("terms"):
        print(f"✓ Extracted {len(result['terms'])} terms")


def test_technical_terms_mixed(extractor):
    """Test mix of real and fake technical terms."""
    text = """
    Quantum entanglement in superconducting qubits.
    We achieve T1 times of 200 microseconds using transmon architecture.
    """
    
    system_prompt = """You are a precise information extraction assistant.
- Return ONLY valid JSON
- Extract ONLY information explicitly present in the source text
- Do NOT invent, guess, or hallucinate any information
- If information is not present, use null or empty array"""

    user_prompt = """Extract the following technical terms ONLY if they appear in the text:

Expected JSON format:
{
  "quantum_terms": ["string"] | null,
  "ml_terms": ["string"] | null
}

Look for these specific terms:
- Quantum terms: "quantum entanglement", "superconducting qubits", "transmon"
- ML terms: "neural networks", "GPU acceleration"

Return only terms that are actually present. Use null or empty array if none found."""
    composed_user = _with_text(user_prompt, text)
    
    result = extractor.extract_one(
        text,
        system_prompt=system_prompt,
        user_prompt=composed_user,
        verify=True,
        token_threshold=0.6,
    )
    
    log_comparison(
        "Technical Terms - Mixed",
        text,
        system_prompt,
        composed_user,
        extractor.last_raw_output,
        extractor.last_verified_output
    )
    
    # Quantum terms should be present
    if result.get("quantum_terms"):
        quantum_terms = [t for t in result["quantum_terms"] if t]
        assert len(quantum_terms) > 0
    
    # ML terms should be absent (null or empty)
    ml_terms = result.get("ml_terms")
    if ml_terms:
        valid_ml_terms = [t for t in ml_terms if t]
        assert len(valid_ml_terms) == 0


def test_empty_text(extractor):
    """Test empty text handling."""
    result = extractor.extract_one("", user_prompt="Extract anything")
    
    print(f"\n{'='*80}")
    print(f"TEST: Empty Text Handling")
    print(f"{'='*80}")
    print(f"\nSOURCE TEXT: (empty)")
    print(f"\nRESULT:")
    print(json.dumps(result, indent=2))
    print(f"{'='*80}\n")
    
    assert result.get("error") == "empty_text"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])