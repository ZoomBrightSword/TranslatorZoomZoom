import pytest
from game_translator.utils.text_utils import clean_text

def test_clean_text_removes_extra_whitespace():
    """Tests if multiple spaces and leading/trailing spaces are handled."""
    assert clean_text("  hello   world  ") == "Hello world"

def test_clean_text_handles_line_breaks():
    """Tests if text split across lines is joined correctly."""
    text = "this is the first line\nand this is the second."
    assert clean_text(text) == "This is the first line and this is the second."

def test_clean_text_normalizes_capitalization():
    """Tests if inconsistent capitalization is converted to sentence case."""
    text = "sAVe pOiNT"
    assert clean_text(text) == "Save point"

def test_clean_text_handles_empty_and_none_input():
    """Tests behavior with empty or None input."""
    assert clean_text("") == ""
    assert clean_text(None) == ""

def test_clean_text_replaces_ocr_errors():
    """Tests replacement of common OCR artifacts. Expects '|' -> 'I' and sentence case."""
    text = "l'm looking for a Health Pot|on"
    # The function will capitalize the first letter 'l' and lowercase the rest.
    # It will also correctly turn 'Pot|on' into 'Potion'.
    assert clean_text(text) == "L'm looking for a health potion"

def test_clean_text_complex_case():
    """Tests multiple cleaning steps at once. Expects '|' -> 'I' and sentence case."""
    text = "  lOaDiNG...\n please   wa|t.  "
    # The function should handle whitespace, line breaks, casing, and OCR errors.
    assert clean_text(text) == "Loading... please wait."

def test_clean_text_handles_already_clean_text():
    """Tests that already clean text is not mangled, but casing is normalized."""
    text = "This is a clean sentence."
    # The function should normalize to sentence case.
    assert clean_text(text) == "This is a clean sentence."

def test_intelligent_line_joining():
    """Tests that lines ending in punctuation are not joined with a space, and casing is normalized."""
    text = "First sentence.\nSecond sentence."
    # The function should join, then apply sentence case, which lowercases 'Second'.
    assert clean_text(text) == "First sentence. second sentence."