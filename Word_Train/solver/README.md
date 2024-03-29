# Word Train Solver

The code here is for "solving" n-player Word Train for a given lexicon.

In other words, given the current running word, what letter should the current player play next?

## To Run

From the /Word_Train diectory, run:

`python3 -m solver.word_train_solver <path/to/lexicon.txt> -w <current running word> [-n <how many players, default = 2>] [-m <minimum word length, default = 4>]`

Examples:

`python3 -m solver.word_train_solver ./lexicons/english.txt -w appl`

`python3 -m solver.word_train_solver ./lexicons/english.txt -w appl -n 3`

`python3 -m solver.word_train_solver ./lexicons/english.txt -w appl -n 3 -m 8`
