from domain.autocomplete.tokenizer import tokenize


class TrieNode:
    __slots__ = ('children', 'is_word')

    def __init__(self):
        self.children: dict[str, TrieNode] = {}
        self.is_word: bool = False

class TrieNode:
    __slots__ = ('children', 'is_word')

    def __init__(self):
        self.children: dict[str, TrieNode] = {}
        self.is_word: bool = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        """
        Insert a word into the Trie.
        """
        node = self.root
        for char in word:
            node = node.children.setdefault(char, TrieNode())
        node.is_word = True

    def autocomplete(self, prefix: str, limit: int | None = None) -> list[str]:
        """
        Given a prefix, return a list of words that start with that prefix.
        If the prefix consists of multiple words, tokenize it and provide autocomplete
        results for each individual word in the prefix.

        Args:
            prefix (str): The prefix or input string to autocomplete.
            limit (int | None): The maximum number of suggestions to return.

        Returns:
            list[str]: List of autocomplete suggestions.
        """
        # Tokenize the prefix into words
        tokens = tokenize(prefix.lower())

        # Set to store results and avoid duplicates
        results = set()

        # For each token, get autocomplete suggestions
        for token in tokens:
            node = self._find_node(token)
            if node:
                self._dfs(node, token, results, limit)

        # Limit the number of results to the specified limit
        return list(results)[:limit] if limit else list(results)

    def _find_node(self, prefix: str) -> TrieNode | None:
        """
        Find the TrieNode corresponding to the end of a given prefix.

        Args:
            prefix (str): The prefix to search for in the Trie.

        Returns:
            TrieNode | None: The TrieNode corresponding to the prefix or None if not found.
        """
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def _dfs(self, node: TrieNode, prefix: str, results: set[str], limit: int | None) -> None:
        """
        Perform a depth-first search (DFS) from the given node to collect words.

        Args:
            node (TrieNode): The starting node for DFS.
            prefix (str): The current prefix being built.
            results (set[str]): The set to store found words.
            limit (int | None): The maximum number of results to return.
        """
        # If the current node represents a word, add it to the results
        if node.is_word:
            results.add(prefix)
            if limit and len(results) >= limit:
                return

        # Recursively explore the children of the current node
        for char, child in node.children.items():
            if limit and len(results) >= limit:
                return
            self._dfs(child, prefix + char, results, limit)

