import argparse
import random

from base_classes.lexicon import LanguageLexicon
from solver.word_train_solver import WordTrainSolver

MINIMUM_WORD_LENGTH = 4


# The was all coded in like fifteen minutes, so it is awful and needs refactoring
# I just wanted to spin it up quickly since all of the pieces were in place already
def game_loop(
    lexicon: LanguageLexicon,
    solver: WordTrainSolver,
    allowable_letters: set[str],
    player_goes_first: bool,
) -> None:
    players_turn = player_goes_first
    word = ""
    node = lexicon.trie.root
    while True:
        if players_turn:
            print(f"\nCurrent word: {word}")
            letter = input("Choose a letter: ")
        else:
            print("\nChoosing a letter ...")
            if word == "":
                # Choose randomly at the beginning
                letter = random.choice(list(allowed_letters))
            else:
                solution = solver.solve(word, 2)
                # Very basic logic
                if solution.possible_wins:
                    letter = random.choice(solution.possible_wins)
                elif solution.certain_wins:
                    letter = random.choice(solution.certain_wins)
                else:
                    letter = random.choice(list(node.children.keys()))
        node = node.children.get(letter)
        if not node:
            print(f"\nYou lose :( ({word + letter} does not lead to a valid word)")
            valid_words = [
                word
                for word in lexicon.trie.get_all_words(word)
                if len(word) >= MINIMUM_WORD_LENGTH
            ]
            print(f"\nI was thinking {valid_words[0]}")
            break
        word += letter
        if node.is_leaf and len(word) >= MINIMUM_WORD_LENGTH:
            print(f"\nFinal Word: {word}")
            if players_turn:
                print("\nYou win!")
            else:
                print("\nI got there first! You lose :(")
            break
        players_turn = not players_turn
    inp = input("Play Again? (Y)es (N)o: ")
    if inp.lower() == "y":
        game_loop(lexicon, solver, allowable_letters, not player_goes_first)
    else:
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Word Train",
        description="The game Word Train",
    )
    parser.add_argument(
        "-f",
        "--first",
        help="Whether the current player goes first (t)rue/(f)alse",
        default="t",
    )
    parser.add_argument(
        "-l", "--lexicon", help="What lexicon to load", default="./lexicons/english.txt"
    )
    args = parser.parse_args()
    print("\nLoading lexicon ... ")
    lexicon = LanguageLexicon(args.lexicon)
    allowed_letters = lexicon.characters  # Calculate this here
    print("\n==Word Train==")
    game_loop(lexicon, WordTrainSolver(lexicon), allowed_letters, "t" in args.first)
