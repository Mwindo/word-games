from base_classes.lexicon import LanguageLexicon
import dataclasses
import itertools


class WordTrainSolver:

    @dataclasses.dataclass
    class WordTrainSolution:
        prefix: str
        certain_wins: list[str]  # Wins that are guaranteed with perfect play
        possible_wins: list[str]  # Wins that rely on how the other players play
        # certain_win_words: list[str]  # End words for the letters in certain_wins
        # possible_win_words: list[str]  # End words for the letters in possible_wins

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
        Given the current prefix, solve returns a list of possible next letters that a player
        could play such that, if they play perfectly, they are guaranteed a win.
        If no such letters exist, solve returns an empty list.

        Example:
        solve('appl', 2, 4) --> [e, y, a] because 'apple' and 'apply' are automatic wins,
        and the only 'appla' words are 'applause' and 'applausive...', each of which
        is a winning word for the current player.
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
            next_letter_option = word[len(prefix)]  # TODO: handle error
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
        winning_words_lexicon = LanguageLexicon(winning_words)
        losing_words_lexicon = LanguageLexicon(
            itertools.chain.from_iterable(losing_words.values())
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
                    # For every possible losing word, we need to consider the prefixes
                    # that can arise from any combination of player choices until the
                    # current player's next choice.
                    # (Why only these choices? Because we have shown that,
                    # whatever the other players choose next, the current player can be
                    # guaranteed a win--regardless of what happens later.)
                    losing_prefixes = [
                        losing_word[: len(next_letter_prefix) + i]
                        for i in range(1, num_players)
                    ]
                    # For each of these losing prefixes, we need to check if we
                    # can find a winning word that comes before the losing word.
                    # Otherwise, there is a route to a non-winning word regardless
                    # of perfect play.
                    for losing_prefix in losing_prefixes:
                        found = False
                        for word in winning_words_lexicon.trie.get_all_words(
                            losing_prefix
                        ):
                            if len(word) < len(losing_word):
                                # We've found a winning word we can get to before the losing word.
                                found = True
                                break
                        if not found:
                            # We didn't find a winning word we can get to before the losing word,
                            # so possible_next_letter is not a guaranteed win for the current player.
                            certain_wins.remove(next_letter_option)
                            break
                    if next_letter_option not in certain_wins:
                        # We've already eliminated possible_next_letter, so no need to keep
                        # checking
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
    lexicon = LanguageLexicon("./lexicons/english.txt")
    solver = WordTrainSolver(lexicon)
    print(
        solver.solve("appl", 2),
    )  # a e y -- I think
    print(
        solver.solve("appli", 2),
    )  # q -- I think
    print(
        solver.solve("applic", 2),
    )  # none
    print(
        solver.solve("ap", 2),
    )  # ['n', 'j', 'y', 'r'] -- I think
    print(
        solver.solve("a", 2),
    )  # ['q', 'v'] -- I think
    # print(
    #     WordTrainSolver(LanguageLexicon("./lexicons/english.txt")).solve("", 2),
    # )  # none
