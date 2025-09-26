import re

def clean_text(text: str) -> str:
    """
    Cleans raw OCR text to make it more suitable for translation.

    - Replaces common OCR errors.
    - Joins words that are split across lines.
    - Normalizes whitespace and capitalization.

    Args:
        text (str): The raw text from OCR.

    Returns:
        str: The cleaned text.
    """
    if not text:
        return ""

    # 1. Replace common OCR misinterpretations
    text = text.replace('|', 'I').replace('`', "'").replace('‘', "'")

    # 2. Join lines intelligently
    # This is a simple heuristic. More advanced logic could be used.
    lines = text.splitlines()
    rejoined_lines = []
    if lines:
        rejoined_lines.append(lines[0])
        for i in range(1, len(lines)):
            prev_line = rejoined_lines[-1].strip()
            current_line = lines[i].strip()
            if not current_line:
                continue
            # Join if previous line doesn't end with sentence-ending punctuation
            if prev_line and prev_line[-1] not in ".!?":
                rejoined_lines[-1] = prev_line + " " + current_line
            else:
                rejoined_lines.append(current_line)

    text = " ".join(rejoined_lines)

    # 3. Normalize whitespace (remove multiple spaces, newlines, tabs)
    text = re.sub(r'\s+', ' ', text).strip()

    # 4. Capitalize the first letter of the sentence for consistency.
    # This helps translation models that are sensitive to casing.
    if len(text) > 1:
        text = text[0].upper() + text[1:].lower()

    return text