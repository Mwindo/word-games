import argparse
import random

from base_classes.lexicon import LanguageLexicon
from solver.word_train_solver import WordTrainSolver

MINIMUM_WORD_LENGTH = 4


def start_game(lexicon_file_path: str, player_goes_first: bool):
    print("\nLoading lexicon ... ")
    lexicon = LanguageLexicon(lexicon_file_path)
    allowed_letters = lexicon.characters  # Calculate this here to avoid loading later
    print("\n==Word Train==")
    game_loop(lexicon, WordTrainSolver(lexicon), allowed_letters, player_goes_first)


def game_loop(
    lexicon: LanguageLexicon,
    solver: WordTrainSolver,
    allowable_letters: set[str],
    player_goes_first: bool,
) -> None:
    """
    Loop until the game ends, alternating between prompting the user
    for the next letter and letting the computer choose the next letter.
    """
    # TODO: We can maybe make this more efficient by not re-solving every time?
    players_turn = player_goes_first
    word = ""
    node = lexicon.trie.root

    def get_letter(word: str) -> str:
        if players_turn:
            return get_player_letter(word)
        return get_computer_letter(word)

    def get_player_letter(word: str) -> str:
        print(f"\nCurrent word: {word}")
        letter = input("Choose a letter: ")
        return letter

    def get_computer_letter(word: str) -> str:

        def get_valid_initial_letters() -> list[str]:
            return [key for key in node.children if node.children[key].children]

        print("\nChoosing a letter ...")
        if not word:
            # Choose randomly at the beginning
            return random.choice(get_valid_initial_letters())
        solution = solver.solve(word, 2)
        # Very basic logic: we choose letters that work,
        # but we avoid certain wins when possible to give
        # the player a chance to win
        if solution.possible_win_words:
            letter = random.choice(solution.possible_win_letters)
        elif solution.certain_win_words:
            letter = random.choice(solution.certain_win_letters)
        else:
            letter = random.choice(list(node.children.keys()))
        return letter

    def handle_invalid_letter(word: str, invalid_letter: str) -> None:
        print(f"\nI win!")
        valid_words = [
            word
            for word in lexicon.trie.get_all_words(word)
            if len(word) >= MINIMUM_WORD_LENGTH
        ]
        print(
            f"({word + invalid_letter} does not lead to a valid word. "
            f"I was thinking {valid_words[0]}.)"
        )

    def handle_winning_word(word: str) -> None:
        print(f"\nFinal Word: {word}")
        if players_turn:
            print("\nYou win!")
        else:
            print("\nI got there first! I win!")

    def letter_is_valid(letter: str) -> bool:
        return node.is_leaf or node.children

    # Loop until we reach the end of the word or until we reach an invalid string
    while True:
        letter = get_letter(word)
        node = node.children.get(letter)  # Iterate through the prefix tree
        if not node or not letter_is_valid(letter):
            # The letter that was received does not work
            handle_invalid_letter(word, letter)
            break
        word += letter  # Update the running word
        if node.is_leaf and len(word) >= MINIMUM_WORD_LENGTH:
            # The letter received wins the game
            handle_winning_word(word)
            break
        players_turn = not players_turn

    # End of game
    inp = input("\nPlay Again? (Y)es (N)o: ")
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
    start_game(args.lexicon, "t" in args.first)
