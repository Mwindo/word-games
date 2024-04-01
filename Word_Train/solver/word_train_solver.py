import argparse
from dataclasses import dataclass, field

from base_classes.lexicon import LanguageLexicon, TrieNode


DEFAULT_MINIMUM_WORD_LENGTH = 4


class WordTrainSolver:

    def __init__(
        self,
        lexicon: LanguageLexicon,
    ) -> None:
        self.lexicon = lexicon

    @dataclass
    class WordTrainSolution:
        """
        The class corresponding to the return value of solve.
        """

        # Words that occur on the player's turn that the player can get to
        # (as a set, not necessarily any particular word) regardless of other
        # players' choices
        certain_win_words: set[str]

        # Words that occur on the player's turn that depend on other players' choices
        possible_win_words: set[str]

        # Words that do not occur on the player's turn
        losing_words: set[str]

        # The next letter choices that lead, with perfect play, to a win
        certain_win_letters: list[str] = field(default_factory=lambda: set())

        # The next letter choices that lead, depending on other players' choices, to a win
        possible_win_letters: list[str] = field(default_factory=lambda: set())

        # The next letter choices that lead only to losses
        losing_letters: list[str] = field(default_factory=lambda: set())

    def _solve_recursive(
        self,
        original_prefix: str,
        current_prefix: str,
        current_prefix_node: TrieNode,
        num_players: int,
        min_word_length: int,
    ) -> tuple[
        set[str], set[str], set[str]
    ]:  # Certain wins, possible wins, unavoidable losses
        """
        Recurse through the lexicon Trie, accumulating words that are certain wins,
        possible wins, and (unavoidable) losses.
        :param original_prefix: the prefix from which we started the solve procedure
        :param current_prefix: the prefix for which we are currently solving
        :param current_prefix_node: the node corresponding to current_prefix in our Trie
        :param num_players: the number of players in the game
        :param min_word_length: the minimum number of characters in a final word
        """
        # turn is an integer representing whose turn it is
        turn = (len(current_prefix) - len(original_prefix)) % num_players
        was_just_players_turn = turn == 1  # If the player made the last choice
        if current_prefix_node.is_leaf and len(current_prefix) >= min_word_length:
            if (
                was_just_players_turn
            ):  # The final word happened on the current player's turn
                return (set([current_prefix]), set(), set())
            else:  # The final word happened on another player's turn
                return (set(), set(), set([current_prefix]))

        certain_wins = set()
        possible_wins = set()
        unavoidable_losses = set()

        # We will recurse through the Trie, updating certain_wins, possible_wins,
        # and losses
        for letter in current_prefix_node.children:
            wins, possibles, losses = self._solve_recursive(
                original_prefix,
                current_prefix + letter,
                current_prefix_node.children[letter],
                num_players,
                min_word_length,
            )
            certain_wins = certain_wins.union(wins)
            possible_wins = possible_wins.union(possibles)
            unavoidable_losses = unavoidable_losses.union(losses)
        is_players_turn = turn == 0  # If the player is making the current choice
        if is_players_turn:
            # If it's the current player's turn and they have a path to a guaranteed
            # win, then they can avoid all losses
            if certain_wins:
                unavoidable_losses = set()
        else:
            # If it's not the current player's turn and there are ways for the current
            # player to lose, then the current player cannot be guaranteed to avod
            # those losses. Thus, at best, the wins they have available are only possible
            # wins, not certain.
            if unavoidable_losses:
                possible_wins = possible_wins.union(certain_wins)
                certain_wins = set()
        return (certain_wins, possible_wins, unavoidable_losses)

    def solve(
        self,
        prefix: str,
        num_players: int,
        min_word_length: int = DEFAULT_MINIMUM_WORD_LENGTH,
    ) -> WordTrainSolution:
        """
        "Solve" Word Train. Returns a WordTrainSolution instance.
        :param prefix: the prefix to solve from
        :param num_players: the number of players in the game
        :min_word_length: the minimum number of letters a final word must be
        """
        # First, recurse over the lexicon Trie, starting at prefix, to get
        # the wins, and possible that can occur with perfect play.
        # We ignore losses because we will re-calculate losses to include all
        # losing words, not just losses that would only occur with perfect play.
        certain_win_words, possible_win_words, _ = self._solve_recursive(
            prefix,
            prefix,
            self.lexicon.trie.get_prefix_node(prefix),
            num_players,
            min_word_length,
        )
        # Recalculate losing words to include all losing words, not just
        # unavoidable losses.
        losing_words = {
            word
            for word in self.lexicon.trie.get_all_words(
                prefix, stop_at_leaf=True, min_length=min_word_length
            )
            if (len(word) - len(prefix)) % num_players != 1
        }
        # Get the next letter options that lead to wins, possible wins, and unavoidable losses.
        win_letters = {word[len(prefix)] for word in certain_win_words}
        possible_win_letters = {
            word[len(prefix)] for word in possible_win_words
        } - win_letters
        losing_letters = {
            letter
            for letter in self.lexicon.characters
            if letter not in win_letters and letter not in possible_win_letters
        }
        return WordTrainSolver.WordTrainSolution(
            certain_win_words,
            possible_win_words,
            losing_words,
            list(sorted(win_letters)),
            list(sorted(possible_win_letters)),
            list(sorted(losing_letters)),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Word Train Solver",
        description="A solver for the game Word Train",
    )
    parser.add_argument(
        "lexicon", help="Specify the file containing line-separated words"
    )
    parser.add_argument("-w", "--word", required=True, help="The current running word")
    parser.add_argument(
        "-n",
        "--num_players",
        required=False,
        help="The number of players in the game",
        default=2,
    )
    parser.add_argument(
        "-m",
        "--min_word_length",
        required=False,
        help="The minimum word length for a winning word",
        default=4,
    )
    args = parser.parse_args()
    print("\nLoading lexicon ... ")
    lexicon = LanguageLexicon(args.lexicon)
    print("\nSolving ...")
    print(
        WordTrainSolver(lexicon).solve(
            args.word, int(args.num_players), int(args.min_word_length)
        )
    )
