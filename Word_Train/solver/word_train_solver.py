import argparse
import dataclasses
import itertools

from base_classes.lexicon import LanguageLexicon


class WordTrainSolver:

    @dataclasses.dataclass
    class WordTrainSolution:
        prefix: str
        certain_wins: list[str]  # Wins that are guaranteed with perfect play
        possible_wins: list[str]  # Wins that rely on how the other players play
        # certain_win_words: list[str]  # End words for the letters in certain_wins
        # possible_win_words: list[str]  # End words for the letters in possible_wins
        # probabilities (given random choices) would be great too

        def __str__(self):
            return (
                f"certain wins for {self.prefix}:\n{self.certain_wins}\n"
                f"possible wins for {self.prefix}:\n{self.possible_wins}"
            )

    def __init__(
        self,
        lexicon: LanguageLexicon,
    ) -> None:
        self.lexicon = lexicon

    def _get_certain_wins(
        self, prefix: str, num_players: int, min_word_length: int = 4
    ) -> tuple[list[str], list[str]]:
        pass

    def _get_possible_wins(
        self, prefix: str, num_players: int, min_word_length: int = 4
    ) -> tuple[list[str], list[str]]:
        pass

    # TODO: I believe this function "works"
    # But it's terrible, so let's improve it
    def solve(
        self, prefix: str, num_players: int, min_word_length: int = 4
    ) -> WordTrainSolution:
        """
        Given the current prefix, solve returns a WordTrainSolution instance with
        (possibly empty) lists of letters certain_wins and possible_wins.
        certain_wins are letters that, should the player play perfectly,
        guarantee a win. possible_wins are letters that can lead to a win, but which
        depend on other players' choices.

        Example based on ./lexicons/english.txt:
        solve('appl', 2, 4):
        --> certain_wins ["e", "y", "a"] because "apple" and "apply"
        are automatic wins, and the only "appla" words are "applause" and "applausive...",
        each of which is a winning word for the current player.
        --> possible_wins ["i", "o"] because (e.g.) "application" and "applosion"
        would be winning words, but it depends on the other player not choosing letters
        that would lead to the losing words "appicable" or "applot."
        """

        all_words = self.lexicon.trie.get_all_words(prefix)
        # We store all of the words based on the current prefix that represents wins for us.
        # We also store all of the words based on the current prefix that represent losses for us.
        # We use dicts with the key the next letter and the value a set of options.
        winning_words: set[str] = set()
        possible_winning_letters: set[str] = set()
        losing_words: dict[str, set] = dict()
        for word in all_words:
            if len(word) < min_word_length:
                continue
            next_letter_option = (
                word[len(prefix)] if len(prefix) < len(word) else word[0]
            )
            if (
                len(word) - len(prefix)
            ) % num_players == 1:  # This word happens on the current player's turn
                winning_words.add(word)
                possible_winning_letters.add(next_letter_option)
            else:
                losing_words[next_letter_option] = losing_words.get(
                    next_letter_option, set()
                )
                losing_words[next_letter_option].add(word)
        # We create lexicons so we can use tries for more efficient lookups
        winning_words_lexicon = LanguageLexicon(winning_words or [])
        losing_words_lexicon = LanguageLexicon(
            itertools.chain.from_iterable(losing_words.values()) or []
        )
        # We start our search for solutions by looking at all of the next letters
        # that can lead to a winning word (note that there is no guarantee that we can
        # get to this word, e.g., plant will come before plants even if plants is
        # "winning" word for us).
        certain_wins, possible_wins = set(), set()
        for next_letter_option in possible_winning_letters:
            next_letter_prefix = prefix + next_letter_option
            # If the new prefix is a winning word, we are done.
            if next_letter_prefix in winning_words:
                certain_wins.add(next_letter_option)
            # If the new prefix isn't a prefix of any losing word,
            # then we are guaranteed to reach a winning word, and we are done.
            elif not losing_words_lexicon.trie.get_prefix_node(next_letter_prefix):
                certain_wins.add(next_letter_option)
            else:
                # Now things get more complex
                # Tentatively add the solution. (TODO: There is almost certainly a better way.)
                certain_wins.add(next_letter_option)
                # Get all of the losing words that start with the new prefix
                possible_losing_words = losing_words[next_letter_option]
                # For every possible losing word, we will check if there is a winning word
                # that the current player can get to first. If not, then the next letter option
                # we are considering is invalid: even if the player plays perfectly, they
                # might end up at a losing word.
                for losing_word in possible_losing_words:
                    # Get the prefix for the word given the number of players.
                    losing_prefix = losing_word[
                        : len(next_letter_prefix) + num_players - 1
                    ]
                    # We need to check if we can find a winning word that
                    # comes before the losing word.
                    # Otherwise, there is a route to a non-winning word regardless
                    # of perfect play.
                    if not any(
                        len(word) < len(losing_word)
                        for word in winning_words_lexicon.trie.get_all_words(
                            losing_prefix
                        )
                    ):
                        certain_wins.remove(next_letter_option)
                        break
        # TODO: Make this more efficient
        possible_wins = (
            set(
                [
                    word[len(prefix)]
                    for word in winning_words
                    if all(
                        not word.startswith(w)
                        for w in losing_words.get(word[len(prefix)], set())
                    )
                ]
            )
            - certain_wins
        )

        return WordTrainSolver.WordTrainSolution(
            prefix, list(sorted(certain_wins)), list(sorted(possible_wins))
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
