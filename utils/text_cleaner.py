# utils/text_cleaner.py

import re

def clean_text(text: str) -> str:
    """
    Clean document text: remove extra spaces, headers, etc.
    """
    text = re.sub(r"\s+", " ", text)  # Collapse whitespace
    text = text.strip()
    return text
