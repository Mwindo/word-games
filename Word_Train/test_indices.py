from branching_index import (
    LanguageDictionary,
    DictionaryIndexCalculator,
    BinaryBranchingIndex,
    TotalBranchingIndex,
)


def test_binary_branching_index():
    expected = [(1, float(1/7)), (2, .2), (3, float(4/7)), (4, .25)]
    for test_num, expected_val in expected:
        dict_path = f"./dictionaries/d_test_{test_num}.txt"
        ld = LanguageDictionary(dict_path)
        bb = DictionaryIndexCalculator(BinaryBranchingIndex)
        assert bb.calculate_index(ld).index == expected_val


def test_total_branching_index():
    expected = [(1, float(1/7)), (2, .2), (3, float(5/7)), (4, .375)]
    for test_num, expected_val in expected:
        dict_path = f"./dictionaries/d_test_{test_num}.txt"
        ld = LanguageDictionary(dict_path)
        bb = DictionaryIndexCalculator(TotalBranchingIndex)
        assert bb.calculate_index(ld).index == expected_val


def test_binary_branching_index_sampled():
    dict_path = "./dictionaries/d_test_random_200_25.txt"
    ld = LanguageDictionary(dict_path)
    bb = DictionaryIndexCalculator(BinaryBranchingIndex)
    result1 = bb.calculate_index_from_samples(ld, 100, 50)
    # result2 is the same as result1 except with a percentage-based sample size
    result2 = bb.calculate_index_from_samples(ld, 100, .25) # .25 * 200 = 50
    # Check that the results we get are "reasonable"
    for result in [result1, result2]:
        assert abs(result.index - 0.028) < .05
        assert result.index_variance < .001
        assert result.index_standard_deviation < .01
    

def test_total_branching_index_sampled():
    dict_path = "./dictionaries/d_test_random_200_25.txt"
    ld = LanguageDictionary(dict_path)
    tb = DictionaryIndexCalculator(TotalBranchingIndex)
    result1 = tb.calculate_index_from_samples(ld, 100, 50)
    # result2 is the same as result1 except with a percentage-based sample size
    result2 = tb.calculate_index_from_samples(ld, 100, .25) # .25 * 200 = 50
    # Check that the results we get are "reasonable"
    for result in [result1, result2]:
        assert abs(result.index - 0.076) < .05
        assert result.index_variance < .001
        assert result.index_standard_deviation < .01
