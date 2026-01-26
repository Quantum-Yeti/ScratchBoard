import re

WORD_RE = re.compile(r"[a-zA-Z0-9]{2,}")

def tokenize(text: str | None) -> set[str]:
    if not text:
        return set()

    return {
        match.group(0).lower()
        for match in WORD_RE.finditer(text)
    }

