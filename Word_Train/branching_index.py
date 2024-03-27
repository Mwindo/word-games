import abc
import random
from typing import TypeVar, Iterable
import dataclasses


class TrieNode:
    """
    A basic implementation of a prefix tree node.
    """

    def __init__(self) -> None:
        self.children = dict()
        self.is_leaf = False


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


class LanguageDictionary:
    """
    A utility class for loading words from a given dictionary
    into different data structures for use by other objects.
    """

    def __init__(self, words_or_path_to_words: str | Iterable[str]) -> None:
        """
        :param words_or_path_to_words: a str representing the path to a dictionary
        or else an iterable of words (for ad hoc dictionaries)
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
            return f"LanguageDictionary for {self._path_to_words}"
        else:
            return f"LanguageDictionary for unknown dictionary with {len(self.words)} words"

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
        words = self._words or self.get_words_from_file(self._path_to_words)
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


class DictionaryIndex(abc.ABC):

    def __init__(self, dictionary: LanguageDictionary) -> None:
        self.dictionary = dictionary

    def calculate(self) -> float:
        raise NotImplementedError()


# Define a type variable that is bound to DictionaryIndex.
DictionaryIndexType = TypeVar("DictionaryIndexType", bound=DictionaryIndex)


class DictionaryTrieIndex(DictionaryIndex):
    """
    An abstract class for calculating properties of a
    dictionary of words based on prefixes.
    """

    def __init__(self, dictionary: LanguageDictionary) -> None:
        super().__init__(dictionary)
        self.trie = self.dictionary.trie


class BinaryBranchingIndex(DictionaryTrieIndex):
    """
    A class to calculate the "binary branching index," a measure
    of how often a given prefix string in a dictionary has more than one
    option for the following position (including '').

    For example, given the following dictionary:
    a
    apple
    There are 6 prefixes: '', 'a', 'ap', 'app', 'appl', 'apple'
    Only 'a' has a "branch": one branch yields 'a' itself, the other 'apple'.
    The average branching over all prefixes is thus 1/6.
    """

    def calculate(self):
        trie_node_stack = [self.trie.root]
        binary_branchings = 0
        total_prefixes = 0
        # We conduct a DFS over all prefixes
        while trie_node_stack:
            node = trie_node_stack.pop()
            total_prefixes += 1
            # The is_leaf check ensures we count the null string
            # as a branching option when applicable (since a node
            # can be a leaf--i.e., a word end--but also the prefix of another word).
            if len(node.children) > (0 if node.is_leaf else 1):
                binary_branchings += 1
            trie_node_stack += [node for node in node.children.values()]
        return binary_branchings / total_prefixes if total_prefixes else 0


class TotalBranchingIndex(DictionaryTrieIndex):
    """
    A class to calculate the "total branching index," a measure
    of how many degrees of freedom, on average, a prefix string in
    a dictionary has for the following position (including '').

    For example, given the following dictionary:
    a
    apple
    b
    c
    There are 8 prefixes: '', 'a', 'ap', 'app', 'appl', 'apple', 'b', 'c'
    Prefix '' has three options ('a', 'b', 'c'), for two degrees of freedom.
    Prefix 'a' has two options ('a' and 'apple') for one degree of freedom.
    The other prefixes are fixed and contribute zero degrees of freedom.
    The average branching over all prefixes is thus (2+1)/8 = 3/8.
    """

    def calculate(self):
        trie_node_stack = [self.trie.root]
        total_branchings = 0
        total_prefixes = 0
        # We conduct a DFS over all prefixes
        while trie_node_stack:
            node = trie_node_stack.pop()
            total_prefixes += 1
            # The is_leaf check ensures we count the null string
            # as a branching option when applicable (since a node
            # can be a leaf--i.e., a word end--but also the prefix of another word).
            # The degrees of freedom will be the number of options - 1 unless this is negative
            # (since negative degrees of freedom is nonsense in this context).
            total_branchings += max(
                len(node.children) if node.is_leaf else len(node.children) - 1, 0
            )
            trie_node_stack += [node for node in node.children.values()]
        return total_branchings / total_prefixes if total_prefixes else 0


class FakeDictionaryMaker:
    """
    A hokey class for generating "fake" dictionaries, i.e.,
    lists of words for testing.
    """

    # TODO: Specify distribution
    def __init__(
        self, language_name: str, num_words: int, longest_word: int = 25
    ) -> None:
        self.language_name = language_name.strip().lower()
        self.num_words = num_words
        self.longest_word = longest_word

    def build_uniformly_random(self):
        """
        Build a random dictionary given simple constraints.
        This does not account for duplicate strings.
        """
        letters = [letter for letter in "abcdefghijklmnopqrstuvwxyz"]
        lines = [""] * self.num_words
        for i in range(self.num_words):
            length = random.randint(1, self.longest_word)
            lines[i] = "".join([random.choice(letters) for _ in range(length)]) + "\n"
        with open(f"./dictionaries/d_{self.language_name}.txt", "w") as file:
            file.writelines(lines)


class DictionaryIndexCalculator:

    @dataclasses.dataclass
    class DictionaryIndexResult:
        index: float
        index_variance: float
        index_standard_deviation: float

    def __init__(self, index: type[DictionaryIndexType]) -> None:
        self.index = index

    def calculate_index(self, dictionary: LanguageDictionary) -> DictionaryIndexResult:
        return DictionaryIndexCalculator.DictionaryIndexResult(
            self.index(dictionary).calculate(), 0, 0
        )

    def calculate_index_from_samples(
        self, dictionary: LanguageDictionary, num_samples: int, sample_size: int | float
    ):
        if isinstance(sample_size, float):
            if sample_size <= 0 or sample_size >= 1:
                raise Exception("expected 0 < sample_size (float) < 1")
            sample_size = int(sample_size * len(dictionary.words))
        return self._calculate_index_from_samples(dictionary, num_samples, sample_size)

    def _calculate_index_from_samples(
        self, dictionary: LanguageDictionary, num_samples: int, sample_size: int
    ) -> DictionaryIndexResult:
        if len(dictionary.words) <= sample_size:
            raise Exception(f"sample_size is too high for {dictionary}")
        total = 0
        indices = [0] * num_samples
        for i in range(num_samples):
            words = random.sample(list(dictionary.words), sample_size)
            custom_dict = LanguageDictionary(words)
            index = self.index(custom_dict).calculate()
            indices[i] = index
            total += index
        mean = total / num_samples
        variance = (
            sum([(sample_index - mean) ** 2 for sample_index in indices]) / num_samples
        )
        return DictionaryIndexCalculator.DictionaryIndexResult(
            mean, variance, variance**0.5
        )

if __name__ == "__main__":
    for language in [
        # "english",
        # "spanish",
        # "french",
        # "italian",
        # "latin",
        # "random_20_25",
        # "random_200_25",
        # "random_2000_25",
        # "random_20000_25",
        # "random_200000_25",
        # "random_2000000_25",
        "test_1",
        "test_2",
        "test_3",
        "test_4",
    ]:
        print(f"===={language}====")
        dict_path = f"./dictionaries/d_{language}.txt"
        ld = LanguageDictionary(dict_path)
        bb = DictionaryIndexCalculator(BinaryBranchingIndex)
        tb = DictionaryIndexCalculator(TotalBranchingIndex)
        binary_index = bb.calculate_index(ld)
        # binary_subset_index = bb.calculate_index_from_samples(ld, 100, 0.2)
        total_index = tb.calculate_index(ld)
        # total_subset_index = tb.calculate_index_from_samples(ld, 100, 0.2)
        print(f"Binary Branching Index for {language}")
        print(binary_index.index)
        print(
            # binary_subset_index.index,
            # binary_subset_index.index_variance,
            # binary_subset_index.index_standard_deviation,
        )
        print("--------")
        print(f"Total Branching Index for {language}")
        print(total_index.index)
        print(
            # total_subset_index.index,
            # total_subset_index.index_variance,
            # total_subset_index.index_standard_deviation,
        )

# faker = FakeDictionaryMaker('random_2000000_25', 2000000)
# faker.build()
