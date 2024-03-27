from base_classes.lexicon import LanguageLexicon

class WordTrainSolver:

    def __init__(self, lexicon: LanguageLexicon) -> None:
        self.lexicon = lexicon
        self.lexicon.load_trie()

    def solve(self, current_prefix: str, num_players: int = 2) -> list[str]:
        '''
        Given a current string, return all of the possible
        letters that, given perfect play, will guarantee
        the player to win.
        '''
        # TODO
        pass
