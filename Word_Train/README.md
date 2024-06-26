# Word Train

The code in this directory is all related in one way or another to the game Word Train.

## Game Description

When I was young, I had a handheld electronic dictionary with a variety of simple games. Among them was the game Word Train. The game works like this: Players alternate taking turns to contribute one letter to a string. The first player who finishes spelling a valid word (usually at least four letters long to avoid trivial cases) wins. Alternatively, the first player to add a letter for which no valid word of sufficient length can be spelled loses.

### Examples

Player 1: "a", current string is "a"\
Player 2: "p", current string is "ap"\
Player 1: "p", current string is "app"\
Player 2: "l", current string is "appl"\
Player 1: "e", current string is "apple," which is a word, so Player 1 wins
\
\
Player 1: "a", current string is "a"\
Player 2: "p", current string is "ap"\
Player 1: "x", current string is "apx," which cannot spell an English word, so Player 2 wins
\
\
Player 1: "x", current string is "x"\
Player 2: "i", current string is "xi", which is only a prefix for "xi" or "xis" (according to the arbitrary dictionary I am using for this contrived example), neither of which is > 4 letters, so Player 1 wins

## Organization

Shared data structures and code go in `./base_classes`. Lexicons (.txt files of line-separated words) go in `./lexicons`. Other modules are for random explorations based on Word Train that can make use of the base classes and lexicons.

## To Play

word_train.py has a very simple implementation of the game.

Run `python3 -m word_train` from this directory. (This will use the default ./lexicons/english.txt lexicon, which is ... idiosyncratic. It has a lot of abstruse words and sometimes misses less obscure words, like "zeitgeist." To specify a different lexicon, add `-l path/to/file.txt`).

## Tests

Run `python3 -m pytest` from this directory.