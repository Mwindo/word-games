import abc
from typing import TypeVar, Iterable


class TrieNode:
    """
    A basic implementation of a prefix tree node.
    """

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = dict()
        self.is_leaf: bool = False


class Trie:
    """
    A basic implementation of a prefix tree.
    """

    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        current = self.root
        for letter in word:
            current.children[letter] = current.children.get(letter, TrieNode())
            current = current.children[letter]
        current.is_leaf = True

    def get_prefix_node(self, prefix: str) -> TrieNode | None:
        current = self.root
        for letter in prefix:
            if letter not in current.children:
                return None
            current = current.children[letter]
        return current

    def get_all_words(self, prefix: str) -> list[str]:
        node = self.get_prefix_node(prefix)
        if not node:
            return []
        nodes = [(node, prefix)]
        words = []
        while nodes:
            node, prefix = nodes.pop()
            if node.is_leaf:
                words.append(prefix)
            for letter in node.children:
                nodes.append((node.children[letter], prefix + letter))
        return words


class LanguageLexicon:
    """
    A utility class for loading words from a given lexicon
    into different data structures for use by other objects.
    """

    def __init__(self, words_or_path_to_words: str | Iterable[str]) -> None:
        """
        :param words_or_path_to_words: a str representing the path to a lexicon
        or else an iterable of words (for ad hoc lexicons)
        """
        self._trie: Trie | None = None
        self._words = set()
        if isinstance(words_or_path_to_words, str):
            self._words = set()
            self._path_to_words = words_or_path_to_words
        else:
            self._words = set(words_or_path_to_words)
            self._path_to_words = ""

    def __str__(self) -> str:
        if self._path_to_words:
            return f"LanguageLexicon for {self._path_to_words}"
        else:
            return f"LanguageLexicon for unknown lexicon with {len(self.words)} words"

    def get_words_from_file(self, filename: str, to_lower: bool = True) -> list[str]:
        words = set()
        with open(filename) as file:
            for line in file.readlines():
                word = line.strip()
                if to_lower:
                    word = word.lower()
                words.add(word)
        return words

    def load_words(self) -> None:
        if self._words:
            raise Exception("words already loaded!")

        self._words = self.get_words_from_file(self._path_to_words)

    def load_trie(self) -> None:
        if self._trie:
            raise Exception("trie already loaded!")

        self._trie = Trie()
        words = self._words
        if not words and self._path_to_words:
            words = self.get_words_from_file(self._path_to_words)
        for word in words:
            self._trie.insert(word)

    @property
    def trie(self) -> Trie:
        if not self._trie:
            self.load_trie()
        return self._trie

    @property
    def words(self) -> set:
        if not self._words:
            self.load_words()
        return self._words


class LexiconIndex(abc.ABC):

    def __init__(self, lexicon: LanguageLexicon) -> None:
        self.lexicon = lexicon

    def calculate(self) -> float:
        raise NotImplementedError()


# Define a type variable that is bound to LexiconIndex.
LexiconIndexType = TypeVar("LexiconIndexType", bound=LexiconIndex)


class LexiconTrieIndex(LexiconIndex):
    """
    An abstract class for calculating properties of a
    lexicon of words based on prefixes.
    """

    def __init__(self, lexicon: LanguageLexicon) -> None:
        super().__init__(lexicon)
        self.trie = self.lexicon.trie
