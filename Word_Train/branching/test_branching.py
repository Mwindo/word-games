from base_classes.lexicon import LanguageLexicon
from branching.branching_index import (
    BinaryBranchingIndex,
    LexiconIndexCalculator,
    TotalBranchingIndex,
)


def get_lexicon_path(lexicon_name: str) -> str:
    return f"./lexicons/{lexicon_name}.txt"


def test_binary_branching_index():
    expected = [(1, float(1 / 7)), (2, 0.2), (3, float(4 / 7)), (4, 0.25)]
    for test_num, expected_val in expected:
        lexicon_path = get_lexicon_path(f"test_{test_num}")
        ld = LanguageLexicon(lexicon_path)
        bb = LexiconIndexCalculator(BinaryBranchingIndex)
        assert bb.calculate_index(ld).index == expected_val


def test_total_branching_index():
    expected = [(1, float(1 / 7)), (2, 0.2), (3, float(5 / 7)), (4, 0.375)]
    for test_num, expected_val in expected:
        lexicon_path = get_lexicon_path(f"test_{test_num}")
        ld = LanguageLexicon(lexicon_path)
        bb = LexiconIndexCalculator(TotalBranchingIndex)
        assert bb.calculate_index(ld).index == expected_val


def test_binary_branching_index_sampled():
    lexicon_path = get_lexicon_path("test_random_200_25")
    ld = LanguageLexicon(lexicon_path)
    bb = LexiconIndexCalculator(BinaryBranchingIndex)
    result1 = bb.calculate_index_from_samples(ld, 100, 50)
    # result2 is the same as result1 except with a percentage-based sample size
    result2 = bb.calculate_index_from_samples(ld, 100, 0.25)  # .25 * 200 = 50
    # Check that the results we get are "reasonable"
    for result in [result1, result2]:
        assert abs(result.index - 0.028) < 0.05
        assert result.index_variance < 0.001
        assert result.index_standard_deviation < 0.01


def test_total_branching_index_sampled():
    lexicon_path = get_lexicon_path("test_random_200_25")
    ld = LanguageLexicon(lexicon_path)
    tb = LexiconIndexCalculator(TotalBranchingIndex)
    result1 = tb.calculate_index_from_samples(ld, 100, 50)
    # result2 is the same as result1 except with a percentage-based sample size
    result2 = tb.calculate_index_from_samples(ld, 100, 0.25)  # .25 * 200 = 50
    # Check that the results we get are "reasonable"
    for result in [result1, result2]:
        assert abs(result.index - 0.076) < 0.05
        assert result.index_variance < 0.001
        assert result.index_standard_deviation < 0.01
