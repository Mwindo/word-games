import pytest

from .lexicon import LanguageLexicon


# Test we can load a lexicon both with a file path or an iterable of words
def test_loading_lexicon():
    test_1_words = ["apple", "apply"]
    lexicon1 = LanguageLexicon("./lexicons/test_1.txt")
    lexicon2 = LanguageLexicon(test_1_words)
    assert lexicon1.words == lexicon2.words == set(["apple", "apply"])


# Test that we can load a lexicon with no words
# since an empty lexicon is still valid
def test_loading_lexicon_no_words():
    lexicon = LanguageLexicon([])
    assert not lexicon.words


# Test that invalid file paths raises an error on load
def test_loading_lexicon_failure():
    with pytest.raises(FileNotFoundError):
        LanguageLexicon("./fakepath.txt").load_words()


# Test that we get the correct prefix node for our Lexicon trie
def test_trie_get_prefix_node():
    words = ["apple", "applesauce", "application", "apply"]
    lexicon = LanguageLexicon(words)
    node = lexicon.trie.get_prefix_node("appl")
    assert list(sorted(node.children.keys())) == ["e", "i", "y"]
    assert not node.is_leaf
    node = lexicon.trie.get_prefix_node("apple")
    assert node.is_leaf
    assert list(sorted(node.children.keys())) == ["s"]
    node = lexicon.trie.get_prefix_node("apples")
    assert not node.is_leaf
    assert list(sorted(node.children.keys())) == ["a"]


# Test that we get all the correct reachable words in our lexicon based on a given prefix
def test_trie_get_all_words():
    words = ["apple", "applesauce", "application", "apply"]
    lexicon = LanguageLexicon(words)
    assert list(sorted(lexicon.trie.get_all_words(""))) == words
    assert list(sorted(lexicon.trie.get_all_words("a"))) == words
    assert list(sorted(lexicon.trie.get_all_words("ap"))) == words
    assert list(sorted(lexicon.trie.get_all_words("app"))) == words
    assert list(sorted(lexicon.trie.get_all_words("appl"))) == words
    assert lexicon.trie.get_all_words("apply") == ["apply"]
    assert lexicon.trie.get_all_words("apple") == ["apple", "applesauce"]
    assert lexicon.trie.get_all_words("appli") == ["application"]
