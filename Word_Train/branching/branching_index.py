import argparse
import dataclasses
import random

from base_classes.lexicon import LanguageLexicon, LexiconIndexType, LexiconTrieIndex


class BinaryBranchingIndex(LexiconTrieIndex):
    """
    A class to calculate the "binary branching index," a measure
    of how often a given prefix string in a lexicon has more than one
    option for the following position (including '').

    For example, given the following lexicon:
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


class TotalBranchingIndex(LexiconTrieIndex):
    """
    A class to calculate the "total branching index," a measure
    of how many degrees of freedom, on average, a prefix string in
    a lexicon has for the following position (including '').

    For example, given the following lexicon:
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


class FakeLexiconMaker:
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
        Build a random lexicon given simple constraints.
        This does not account for duplicate strings.
        """
        letters = [letter for letter in "abcdefghijklmnopqrstuvwxyz"]
        lines = [""] * self.num_words
        for i in range(self.num_words):
            length = random.randint(1, self.longest_word)
            lines[i] = "".join([random.choice(letters) for _ in range(length)]) + "\n"
        with open(f"./lexicons/d_{self.language_name}.txt", "w") as file:
            file.writelines(lines)


class LexiconIndexCalculator:

    @dataclasses.dataclass
    class LexiconIndexResult:
        index: float
        index_variance: float
        index_standard_deviation: float

        def __str__(self) -> str:
            return (
                f"index: {self.index} "
                f"(variance: {self.index_variance}; "
                f"standard deviation: {self.index_standard_deviation})"
            )

    def __init__(self, index: type[LexiconIndexType]) -> None:
        self.index = index

    def calculate_index(self, lexicon: LanguageLexicon) -> LexiconIndexResult:
        return LexiconIndexCalculator.LexiconIndexResult(
            self.index(lexicon).calculate(), 0, 0
        )

    def calculate_index_from_samples(
        self, lexicon: LanguageLexicon, num_samples: int, sample_size: int | float
    ):
        if isinstance(sample_size, float):
            if sample_size <= 0 or sample_size >= 1:
                raise Exception("expected 0 < sample_size (float) < 1")
            sample_size = int(sample_size * len(lexicon.words))
        return self._calculate_index_from_samples(lexicon, num_samples, sample_size)

    def _calculate_index_from_samples(
        self, lexicon: LanguageLexicon, num_samples: int, sample_size: int
    ) -> LexiconIndexResult:
        if len(lexicon.words) <= sample_size:
            raise Exception(f"sample_size is too high for {lexicon}")
        total = 0
        indices = [0] * num_samples
        for i in range(num_samples):
            words = random.sample(list(lexicon.words), sample_size)
            custom_dict = LanguageLexicon(words)
            index = self.index(custom_dict).calculate()
            indices[i] = index
            total += index
        mean = total / num_samples
        variance = (
            sum([(sample_index - mean) ** 2 for sample_index in indices]) / num_samples
        )
        return LexiconIndexCalculator.LexiconIndexResult(mean, variance, variance**0.5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Branching Index Calculator",
        description="Calculates branching indices for a lexicon",
    )
    parser.add_argument(
        "lexicon", help="Specify the file containing line-separated words"
    )
    parser.add_argument(
        "-t",
        "--types",
        required=True,
        help="What types of indices to run: (b)inary, (t)otal",
    )
    parser.add_argument(
        "-n",
        "--num_samples",
        help="Calculate the index via sampling with this number of samples",
        default=None,
    )
    parser.add_argument(
        "-s",
        "--sample_size",
        help="Specify the sample size to be used if num_samples is specified",
        default=0.25,
    )
    args = parser.parse_args()
    print("\nLoading lexicon ... ")
    lexicon = LanguageLexicon(args.lexicon)
    indices: list[tuple[str, LexiconIndexCalculator]] = []
    if "b" in args.types:
        indices.append(("binary", LexiconIndexCalculator(BinaryBranchingIndex)))
    if "t" in args.types:
        indices.append(("total", LexiconIndexCalculator(TotalBranchingIndex)))
    print("\nSolving ...")
    for index_name, calculator in indices:
        if args.num_samples:
            sample_size = float(args.sample_size)
            if int(sample_size) == sample_size:
                sample_size = int(sample_size)
            index = calculator.calculate_index_from_samples(
                lexicon, int(args.num_samples), sample_size
            )
            print(f"{index_name} {index}")
        else:
            print(f"{index_name} {calculator.calculate_index(lexicon)}")
