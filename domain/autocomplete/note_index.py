from collections import defaultdict
from typing import Iterable

from domain.autocomplete.tokenizer import tokenize
from domain.autocomplete.trie import Trie


class NoteIndex:
    def __init__(self):
        """
        Initialize the NoteIndex, which uses a Trie and an inverted index for efficient search and autocomplete.
        """
        self.trie = Trie()
        self.word_to_notes: dict[str, set[str]] = defaultdict(set)

    def index_note(
        self,
        note_id: str,
        title: str,
        content: str,
        tags: Iterable[str] | None = None
    ) -> None:
        """
        Index a note by extracting words from the title, content, and tags.

        Args:
            note_id (str): The unique ID of the note.
            title (str): The title of the note.
            content (str): The content of the note.
            tags (Iterable[str] | None): A list of tags associated with the note.
        """
        words = set()

        # Tokenize the title and content to get the words
        words |= tokenize(title)
        words |= tokenize(content)

        # If tags are provided, tokenize them as well
        if tags:
            for tag in tags:
                words |= tokenize(tag)

        # Insert the words into the Trie and map them to the note_id
        for word in words:
            self.trie.insert(word)
            self.word_to_notes[word].add(note_id)

    def remove_note(self, note_id: str) -> None:
        """
        Remove a note from the index by deleting its associated words from the Trie and inverted index.

        Args:
            note_id (str): The unique ID of the note to remove.
        """
        # Retrieve the words associated with the note_id
        words = self.word_to_notes.pop(note_id, set())

        # For each word, remove the note_id from the Trie and inverted index
        for word in words:
            if word in self.trie:
                self.trie[word].discard(note_id)
                if not self.trie[word]:
                    del self.trie[word]

    def autocomplete(self, prefix: str, limit: int | None = None) -> list[str]:
        """
        Get autocomplete suggestions for a given prefix.

        Args:
            prefix (str): The prefix to autocomplete.
            limit (int | None): The maximum number of suggestions to return.

        Returns:
            list[str]: A list of autocomplete suggestions.
        """
        return self.trie.autocomplete(prefix, limit)

    def notes_for_word(self, word: str) -> set[str]:
        """
        Retrieve all notes associated with a specific word.

        Args:
            word (str): The word to search for.

        Returns:
            set[str]: A set of note IDs associated with the word.
        """
        return self.word_to_notes.get(word, set())



