import re

def clean_text(text: str) -> str:
    """
    Cleans raw OCR text to make it more suitable for translation.

    - Replaces common OCR errors (e.g., '|' with 'l' or 'I').
    - Joins words that are split across lines.
    - Removes excessive whitespace and non-standard characters.

    Args:
        text (str): The raw text from OCR.

    Returns:
        str: The cleaned text.
    """
    if not text:
        return ""

    # 1. Replace common OCR misinterpretations
    text = text.replace('|', 'I').replace('`', "'")

    # 2. Join lines that seem to be part of the same sentence.
    # A simple heuristic: if a line ends with a lowercase letter and the next
    # starts with one, they are likely part of the same sentence.
    lines = text.splitlines()
    rejoined_lines = []
    if lines:
        rejoined_lines.append(lines[0])
        for i in range(1, len(lines)):
            prev_line = rejoined_lines[-1]
            current_line = lines[i]
            # Check if the previous line likely ends mid-word/sentence
            if prev_line and prev_line.strip() and prev_line.strip()[-1].isalpha() and \
               current_line and current_line.strip() and current_line.strip()[0].islower():
                rejoined_lines[-1] = prev_line.strip() + " " + current_line.strip()
            else:
                rejoined_lines.append(current_line)

    text = " ".join(rejoined_lines)

    # 3. Remove non-ASCII characters that are often OCR noise, but keep punctuation.
    # This regex keeps letters, numbers, spaces, and common punctuation.
    text = re.sub(r'[^a-zA-Z0-9\s.,!?-]', '', text)

    # 4. Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text