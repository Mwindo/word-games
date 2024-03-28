from base_classes.lexicon import LanguageLexicon
import dataclasses


class WordTrainSolver:

    @dataclasses.dataclass
    class WordTrainSolution:
        prefix: str
        certain_wins: list[str]  # Wins that are guaranteed with perfect play
        possible_wins: list[str]  # Wins that rely on how the other players play

        def __str__(self):
            return (
                f"certain wins for {self.prefix}:\n{self.certain_wins}\n"
                f"possible wins for {self.prefix}:\n{self.possible_wins}"
            )

    def __init__(self, lexicon: LanguageLexicon) -> None:
        self.lexicon = lexicon

    # TODO: I believe this function "works"
    # But it's terrible, so let's improve it
    # TODO: implement "possible wins"
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
        # We store all of the words based on the current prefix that represents wins for us
        winning_words = set(
            [
                word
                for word in all_words
                if len(word) >= min_word_length
                and (len(word) - len(prefix)) % num_players == 1
            ]
        )
        # We also store all of the words based on the current prefix that represent losses for us
        losing_words = set(
            [
                word
                for word in all_words
                if len(word) >= min_word_length
                and (len(word) - len(prefix)) % num_players != 1
            ]
        )
        # We create lexicons so we can use tries for more efficient lookups
        winning_words_lexicon = LanguageLexicon(winning_words)
        losing_words_lexicon = LanguageLexicon(losing_words)
        # We start our search for solutions by looking at all of the next letters
        # that can lead to a winning word (note that there is no guarantee that we can
        # get to this word, e.g., plant will come before plants even if plants is
        # "winning" word for us).
        possible_next_letters = set([word[len(prefix)] for word in winning_words])
        certain_wins = set()
        possible_wins = set()
        for possible_next_letter in possible_next_letters:
            possible_prefix = prefix + possible_next_letter
            # If the new prefix is a winning word, we are done.
            if possible_prefix in winning_words:
                certain_wins.add(possible_next_letter)
            # If the new prefix isn't a prefix of any losing word,
            # then we are guaranteed to reach a winning word, and we are done.
            elif not losing_words_lexicon.trie.get_prefix_node(possible_prefix):
                certain_wins.add(possible_next_letter)
            else:
                # Now things get more complex
                # Tentatively add the solution. (TODO: There is almost certainly a better way.)
                certain_wins.add(possible_next_letter)
                # Get all of the losing words that start with the new prefix
                possible_losing_words = [
                    word
                    for word in losing_words
                    if word[len(prefix)] == possible_next_letter
                ]
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
                        losing_word[: len(possible_prefix) + i]
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
                            certain_wins.remove(possible_next_letter)
                            break
                    if possible_next_letter not in certain_wins:
                        # We've already eliminated possible_next_letter, so no need to keep
                        # checking
                        break
        # TODO: Make this more efficient
        possible_wins = (
            set(
                [
                    word[len(prefix)]
                    for word in winning_words
                    if all(not word.startswith(w) for w in losing_words)
                ]
            )
            - certain_wins
        )

        return WordTrainSolver.WordTrainSolution(
            prefix, list(sorted(certain_wins)), list(sorted(possible_wins))
        )


if __name__ == "__main__":
    print(
        WordTrainSolver(LanguageLexicon("./lexicons/english.txt")).solve("appl", 2),
    )  # a e y -- I think
    print(
        WordTrainSolver(LanguageLexicon("./lexicons/english.txt")).solve("appli", 2),
    )  # q -- I think
    print(
        WordTrainSolver(LanguageLexicon("./lexicons/english.txt")).solve("applic", 2),
    )  # none
    print(
        WordTrainSolver(LanguageLexicon("./lexicons/english.txt")).solve("ap", 2),
    )  # ['n', 'j', 'y', 'r'] -- I think
    print(
        WordTrainSolver(LanguageLexicon("./lexicons/english.txt")).solve("a", 2),
    )  # ['q', 'v'] -- I think
    # print(
    #     WordTrainSolver(LanguageLexicon("./lexicons/english.txt")).solve("", 2),
    # )  # none
