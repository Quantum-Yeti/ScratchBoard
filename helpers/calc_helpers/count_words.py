def count_words(text: str) -> tuple[int, int]:
    """
    Count the number of words and characters in a given string.

    A word is defined as a sequence of non-whitespace characters separated by spaces.
    Characters are counted including spaces and punctuation.

    Parameters:
        text (str): The input string to analyze.

    Returns:
        tuple[int, int]: A tuple containing:
            - number of words in the text
            - number of characters in the text
    """
    # Return - words and - characters if the input text is empty or None
    if not text:
        return 0, 0

    # Count words by splitting the text on whitespace and filtering empty strings
    words = len([w for w in text.split() if w.strip()])

    # Count all characters in the text including spaces and punctuation
    chars = len(text)

    # Return the word count and character count as a tuple
    return words, chars