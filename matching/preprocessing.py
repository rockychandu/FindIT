import re
import string

# Standard English stop words
STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 'will',
    'with', 'the', 'this', 'but', 'they', 'have', 'had', 'what', 'when', 'where',
    'who', 'which', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
    'so', 'than', 'too', 'very', 'can', 'just', 'should', 'now', 'my', 'your'
}

def preprocess_text(text: str) -> str:
    """
    Preprocesses input text:
    - Lowercases text
    - Strips whitespace & normalizes empty input
    - Removes punctuation
    - Removes common stop-words
    - Handles whitespace normalization & duplicate tokens
    """
    if not text or not isinstance(text, str):
        return ""

    # Lowercase
    text = text.lower().strip()
    if not text:
        return ""

    # Replace punctuation with whitespace
    translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    text = text.translate(translator)

    # Tokenize by whitespace
    tokens = text.split()

    # Filter stop words and single char noise
    filtered_tokens = [t for t in tokens if t not in STOP_WORDS and len(t) > 1 or t.isdigit()]

    if not filtered_tokens:
        # Fallback to original tokens if all were filtered
        filtered_tokens = tokens

    return " ".join(filtered_tokens)


def tokenize_text(text: str) -> list[str]:
    """Tokenize and return list of clean tokens."""
    clean = preprocess_text(text)
    return clean.split() if clean else []
