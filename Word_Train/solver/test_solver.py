from base_classes.lexicon import LanguageLexicon

from .word_train_solver import WordTrainSolver


# TODO: Update the tests to include checks for words, since the tests here were
# originally for when word_train_solver only returned letters.


# Snapshot with a "real" dictionary
def test_solver_english_words_two_player():
    lexicon = LanguageLexicon("./lexicons/english_test.txt")
    solver = WordTrainSolver(lexicon)
    for prefix, expected_certain, expected_possible in [
        ("appl", ["a", "e", "y"], ["i", "o"]),
        ("appli", ["q"], ["a", "c"]),
        ("applic", ["a"], []),
        (
            "ap",
            ["j", "n", "r", "y"],
            ["a", "e", "h", "i", "l", "o", "p", "s", "t", "u"],
        ),
        ("a", ["q", "v"], [letter for letter in "abcdefghijklmnoprstuwxyz"]),
    ]:
        solution = solver.solve(prefix, 2)
        assert solution.certain_win_letters == expected_certain
        assert solution.possible_win_letters == expected_possible


# Test certain wins in the next position are found
def test_trivial_solution():
    lexicon = LanguageLexicon(["apple", "apply", "applesauce"])
    solver = WordTrainSolver(lexicon)
    solution = solver.solve("appl", 2)
    assert solution.possible_win_letters == []
    assert solution.certain_win_letters == ["e", "y"]


# Test solutions for "fixed" lexicons (where choices don't matter) are handled properly
def test_solver_deterministic():
    lexicons = [LanguageLexicon(["a"]), LanguageLexicon(["aaa"])]
    for lexicon in lexicons:
        solver = WordTrainSolver(lexicon)
        win_solution = solver.solve("", 2, 1)
        lose_solution = solver.solve("a", 2, 1)
        assert win_solution.certain_win_letters == ["a"]
        assert win_solution.possible_win_letters == []
        assert lose_solution.certain_win_letters == []
        assert lose_solution.possible_win_letters == []


# Test that unreachable winning words aren't registered as potential wins
def test_solver_multiple_players_winning_word_unreachable():
    words = [
        "abcdf",
        "abcdftg",
    ]
    lexicon = LanguageLexicon(words)
    solver = WordTrainSolver(lexicon)
    solution = solver.solve("", 3)
    # Even though 'abcdftg' is a winning word, the current
    # player won't be able to reach it
    assert solution.certain_win_letters == solution.possible_win_letters == []


# Test the distinction between possible and certain wins
# and make sure the possible win is registered as certain
# or disappears once the branch separating possible from certain
# is crossed.
def test_solver_multiple_players_winning_word_uncertain():
    words = [
        "abcdfr",
        "abcdftg",
    ]
    lexicon = LanguageLexicon(words)
    solver = WordTrainSolver(lexicon)
    solution_beginning = solver.solve("", 3)
    solution_middle = solver.solve("abc", 3)
    solution_end_win = solver.solve("abcdft", 3)
    solution_end_lose = solver.solve("abcdfr", 3)

    # 'abcdftg' is a winning word, but it depends on
    # the player before choosing t instead of r
    assert (
        solution_beginning.certain_win_letters
        == solution_middle.certain_win_letters
        == []
    )
    assert solution_beginning.possible_win_letters == ["a"]
    assert solution_middle.possible_win_letters == ["d"]
    assert solution_end_win.possible_win_letters == []
    assert solution_end_win.certain_win_letters == ["g"]
    assert (
        solution_end_lose.certain_win_letters
        == solution_end_lose.possible_win_letters
        == []
    )


# Test that certain and possible wins are caught simultaneously.
def test_solver_multiple_players_certain_and_possible_wins():
    words = [
        "mercury",
        "mercur",
        "mars",
        "marzipan",
        "marseilles",
        "venus",
        "venuses",
        "earth",
        "earthy",
        "earns",
        "jupiter",
        "jump",
        "saturn",
        "saturnine",
        "saturnalia",
        "uranus",
        "understand",
        "neptune",
        "nepotism",
    ]
    lexicon = LanguageLexicon(words)
    solver = WordTrainSolver(lexicon)
    solution = solver.solve("", 3)
    assert solution.certain_win_letters == ["j", "n"]  # jump, jupiter, neptune
    assert solution.possible_win_letters == [
        "m",
        "u",
    ]  # mars, mercury, understand


# Test player loses if they never get a chance to play again
def test_player_never_gets_another_turn():
    words = [
        "abcdefghijk",
        "abcdefghijkl",
        "abcdefghijklm",
        "abcdefghijklmn",
        "abcdefghijklmno",
        "abcdefghijklmnop",
    ]
    lexicon = LanguageLexicon(words)
    solver = WordTrainSolver(lexicon)
    solution = solver.solve("", 12)
    assert solution.certain_win_letters == solution.possible_win_letters == []


# Test that no solutions exist for lexicons with no valid words
def unwinnable_lexicon():
    lexicon = LanguageLexicon(["a", "z"])
    solver = WordTrainSolver(lexicon)
    solution1 = solver.solve("a", 2)
    solution2 = solver.solve("", 2)
    for solution in [solution1, solution2]:
        assert solution.possible_win_letters == solution.certain_win_letters == []


# Test that different numbers of players yields expected results
def test_different_num_players():
    lexicon = LanguageLexicon(["abcdefghijklmnopqrstuvwx"])
    # 24 letters
    solver = WordTrainSolver(lexicon)
    solutions: dict[int, WordTrainSolver.WordTrainSolution] = dict()
    for num_players in range(1, 25):
        solutions[num_players] = solver.solve("a", num_players)
        # 2, 11, 22 are wins
        if num_players in [2, 11, 22]:
            assert solutions[num_players].certain_win_letters == ["b"]
            assert solutions[num_players].possible_win_letters == []
        else:
            assert solutions[num_players].certain_win_letters == []
            assert solutions[num_players].possible_win_letters == []


# Test a game with more than 2-3 players
def test_multiple_options_several_players():
    # Some of these are made up words
    words = [
        "apple",
        "applexors" "applesauce",
        "application",
        "applications",
        "applicable",
        "applicant",
        "applier",
        "appliant",
        "appraises",
        "appsolutely",
    ]
    lexicon = LanguageLexicon(words)
    solver = WordTrainSolver(lexicon)
    # Current player is player 4 among 5 players
    solution = solver.solve("app", 5)
    assert solution.certain_win_letters == ["r"]  # appraises
    assert solution.possible_win_letters == ["l"]  # applexors
    # Now current player is player 1 among 5 players
    solution = solver.solve("appli", 5)
    assert solution.certain_win_letters == []
    assert solution.possible_win_letters == ["c"]  # application
    # Now current player is 2 among 5 players
    solution = solver.solve("applic", 5)
    assert solution.certain_win_letters == solution.possible_win_letters == []
    # Now current player is 3 among 5 players
    solution = solver.solve("applica", 5)
    assert solution.certain_win_letters == solution.possible_win_letters == []
    # Now current player is 4 among 5 players
    solution = solver.solve("applicab", 5)
    assert solution.certain_win_letters == solution.possible_win_letters == []
    # Now current player is 5 among 5 players
    solution = solver.solve("applicabl", 5)
    assert solution.certain_win_letters == ["e"]
    assert solution.possible_win_letters == []


def test_losing_word_longer_than_uncertain_winning_word():
    words = ["abcdef", "abcdfgh"]
    lexicon = LanguageLexicon(words)
    solver = WordTrainSolver(lexicon)
    solution = solver.solve("a", 2)
    assert solution.certain_win_letters == []
    assert solution.possible_win_letters == ["b"]
