import pytest
from smart_library.utils.textnorm import normalize_text

@pytest.mark.parametrize("raw,expected", [
    # Newline flattening + lowercasing + whitespace collapse
    ("Hello\nWorld\r\nTest\rLine", "hello world test line"),
    # Whitespace collapse (spaces, tabs) + trimming edge punct
    ("  A   B\tC  ", "a b c"),
    # Hyphenation artifact cleanup
    ("end - to - end", "end-to-end"),
    ("co- op", "co-op"),
    ("pre -processing", "pre-processing"),
    # Edge punctuation trim (only at edges, not internal)
    ("(hello,)", "hello"),
    ("[hello]", "hello"),
    ("{hello};", "hello"),
    # Combination
    ("\n[Example- Text]\n", "example-text"),
    # Empty input
    ("", ""),
])
def test_normalize_text(raw, expected):
    out = normalize_text(raw)
    print(f"Input: '{raw}' -> Output: '{out}' (expected: '{expected}')")
    assert out == expected