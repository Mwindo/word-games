from base_classes.lexicon import LanguageLexicon
from .word_train_solver import WordTrainSolver


def test_solver_english_words_two_player():
    lexicon = LanguageLexicon("./lexicons/english.txt")
    solver = WordTrainSolver(lexicon)
    for prefix, expected_certain, expected_possible in [
        ("appl", ["a", "e", "y"], ["i", "o"]),
        ("appli", ["q"], ["a", "c"]),
        ("applic", [], ["a"]),
        (
            "ap",
            ["j", "n", "r", "y"],
            ["a", "e", "h", "i", "l", "o", "p", "s", "t", "u"],
        ),
        ("a", ["q", "v"], [letter for letter in "abcdefghijklmnoprstuwxyz"]),
    ]:
        solution = solver.solve(prefix, 2)
        assert solution.certain_wins == expected_certain
        assert solution.possible_wins == expected_possible


def test_solver_deterministic():
    lexicons = [LanguageLexicon(["a"]), LanguageLexicon(["aaa"])]
    for lexicon in lexicons:
        solver = WordTrainSolver(lexicon)
        win_solution = solver.solve("", 2, 1)
        lose_solution = solver.solve("a", 2, 1)
        assert win_solution.certain_wins == ["a"]
        assert win_solution.possible_wins == []
        assert lose_solution.certain_wins == []
        assert lose_solution.possible_wins == []
