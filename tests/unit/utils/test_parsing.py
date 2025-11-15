import pytest
from smart_library.utils.parsing import parse_structured_obj

def test_parse_structured_obj_lenient():
    """Lenient mode: accept JSON, Python literals, and salvaged."""
    test_cases = [
        # Valid JSON objects
        ('{"key": "value"}', ({"key": "value"}, "json_ok")),
        ('{"name": "Alice", "age": 30}', ({"name": "Alice", "age": 30}, "json_ok")),

        # Valid JSON arrays
        ('["apple", "banana", "cherry"]', (["apple", "banana", "cherry"], "json_array")),
        ('[1, 2, 3]', ([1, 2, 3], "json_array")),

        # Valid Python literals
        ("{'key': 'value'}", ({"key": "value"}, "python_literal_dict")),
        ("['apple', 'banana']", (["apple", "banana"], "python_literal_array")),

        # Code-fenced JSON
        ("```json\n{\"key\": \"value\"}\n```", ({"key": "value"}, "json_ok")),
        ("```json\n[1, 2, 3]\n```", ([1, 2, 3], "json_array")),

        # Salvaged JSON blocks inside noise
        ("Some text before {\"key\": \"value\"} and some text after", ({"key": "value"}, "json_salvaged_obj")),
        ("Some text before [1, 2, 3] and some text after", ([1, 2, 3], "json_salvaged_array")),

        # Empty input
        ("", (None, "empty_output")),
        ("   ", (None, "empty_output")),

        # Trailing comma: invalid JSON but valid Python literal
        ("[1, 2, 3,]", ([1, 2, 3], "python_literal_array")),
    ]

    for raw_input, expected in test_cases:
        result = parse_structured_obj(raw_input)
        print(f"[lenient] Input: '{raw_input}' => Output: {result}")
        assert result == expected, f"Failed (lenient) for input: '{raw_input}'"


def test_parse_structured_obj_strict_rejects_incomplete():
    """Strict JSON mode: reject incomplete/invalid JSON."""
    invalid_json_inputs = [
        "{key: value}",               # unquoted key
        "[1, 2, 3,]",                 # trailing comma
        '{"a": 1,}',                  # trailing comma in object
        '{"a": "b"',                  # missing closing brace
        "['a', 'b']",                 # Python literal, not JSON
        "invalid json",
        "```json\n{\"a\":1,}\n```",   # code-fenced but invalid JSON
    ]

    for raw_input in invalid_json_inputs:
        obj, reason = parse_structured_obj(raw_input, strict_json=True)
        print(f"[strict] Input: '{raw_input}' => Output: ({obj}, '{reason}')")
        assert obj is None, f"Strict mode should reject: {raw_input}"
        # Accept either 'json_invalid' (preferred) or 'unparseable' if future changes
        assert reason in {"json_invalid", "unparseable", "empty_output"}

def test_parse_structured_obj_strict_accepts_valid():
    """Strict JSON mode: accept valid objects and arrays."""
    valid_inputs = [
        ('{"x": 1}', ("json_ok", dict)),
        ('[1, 2, 3]', ("json_array", list)),
        ("```json\n{\"k\": \"v\"}\n```", ("json_ok", dict)),
    ]
    for raw_input, (expected_reason, expected_type) in valid_inputs:
        obj, reason = parse_structured_obj(raw_input, strict_json=True)
        print(f"[strict-valid] Input: '{raw_input}' => Output: ({obj}, '{reason}')")
        assert isinstance(obj, expected_type)
        assert reason == expected_reason

# Run the tests
if __name__ == "__main__":
    pytest.main()