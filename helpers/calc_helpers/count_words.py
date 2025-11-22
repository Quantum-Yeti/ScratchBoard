def count_words(text: str) -> tuple[int, int]:
    if not text:
        return 0, 0

    words = len([w for w in text.split() if w.strip()])
    chars = len(text)

    return words, chars