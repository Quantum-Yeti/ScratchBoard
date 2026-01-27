import re
from typing import Union

from PySide6.QtGui import QTextDocument

def count_words(source: Union[str, QTextDocument]) -> tuple[int, int]:
    """
    Count the number of words and characters.

    - If given a QTextDocument, images/HTML are ignored automatically.
    - If given a string, it is counted as-is.

    Returns:
        (word_count, character_count)
    """
    if not source:
        return 0, 0

    # Normalize input → plain text only
    if isinstance(source, QTextDocument):
        text = source.toPlainText()
    else:
        text = str(source)

    text = text.strip()
    if not text:
        return 0, 0

    # Regex-based word counting to avoid hidden characters
    words = len(re.findall(r'\b\w+\b', text))
    chars = len(text)

    return words, chars