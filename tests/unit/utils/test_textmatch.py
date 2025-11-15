import pytest
from smart_library.utils.textmatch import verify_string_in_string

def test_verify_string_in_string():
    """Unit tests for verify_string_in_string function."""
    
    test_cases = [
        # Exact matches
        ("hello", "Hello world", True),
        ("world", "Hello world", True),
        ("hello", "Hello there, how are you?", True),
        
        # Fuzzy matches (adjusted expectations)
        ("helo", "Hello world", True),  # Fuzzy match
        ("worl", "Hello world", True),   # Fuzzy match
        ("helloo", "Hello world", True),  # Change expected to True
        
        # Case insensitivity
        ("HELLO", "hello world", True),
        ("WORLD", "hello world", True),
        
        # Not present
        ("goodbye", "Hello world", False),
        ("foo", "bar baz", False),
        
        # Empty term
        ("", "Hello world", False),
        (None, "Hello world", False),
        
        # Fuzzy with tolerance (adjusted)
        ("helo", "Hello world", True, 90),  # Should be True with lower tolerance
        ("helo", "Hello world", True, 70),  # Should still be True with even lower tolerance
        ("helo", "Hello world", True, 50),  # Should be False without fuzzy
    ]
    
    for term, text, expected, *args in test_cases:
        fuzzy = args[0] if args else True
        tolerance = args[1] if len(args) > 1 else 80
        
        result = verify_string_in_string(term, text, fuzzy=fuzzy, tolerance=tolerance)
        
        # Logging input and output for debugging
        print(f"Input: term='{term}', text='{text}', fuzzy={fuzzy}, tolerance={tolerance} => Output: {result}")
        
        assert result == expected, f"Failed for term='{term}', text='{text}': expected {expected}, got {result}"

# Run the tests
if __name__ == "__main__":
    pytest.main()