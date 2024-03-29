# Branching Index

## To Run

From the /Word_Train diectory, run:

`python3 -m branching.branching_index <path/to/lexicon.txt> -t <what indices> [-n <how many samples> [-s <sample size in percent (use float) or absolute (use int)>]]`

Examples:

Calculate the binary index over the entire English lexicon:
`python3 -m branching.branching_index ./lexicons/english.txt -t b`

Calculate the total index over the entire English lexicon:
`python3 -m branching.branching_index ./lexicons/english.txt -t bt`

Calculate the binary and total index over the English lexicon via 20 samples, with a sample size of 10000 words:
`python3 -m branching.branching_index ./lexicons/english.txt -t bt -n 20 -s 10000`

Calculate the binary and total index over the English lexicon via 20 samples, with a sample size of 1% of the words:
`python3 -m branching.branching_index ./lexicons/english.txt -t bt -n 20 -s .01`

## Description

While thinking about Word Train, I wondered whether a type of [branching factor](https://en.wikipedia.org/wiki/Branching_factor) might be interesting or useful when applied to lexicons (and, by synecdoche, their parent languages). I called the idea the "branching index." Essentially, the questions I was playing around with were the following: How "fixed" or "determined" is any given prefix of words in some lexicon? How many branches, on average, exist for a given prefix in some lexicon? Would this index yield any interesting synchronic, cross-linguistic insights or diachronic, single-language insights? In other words, to what degree would this index constitute a useful property of a lexicon (and therefore language)?

(I would not be surprised if there is interesting work on this topic. I haven't really investigated deeply; I  wanted to think through things myself first.)

I thought about two related indices. One was the less granular binary index: How often does a given prefix allow for more than one path to a valid word? (E.g., "application" can go to "application" and "applications," so it has 1 branch; "applications" can go only to "applications", so it has no branches.) The other was the more granular "total" index: What are the average degrees of freedom for a prefix? (E.g., "appl" can go to "apply...," "appli...,", "apple...", and "appla..." for three degrees of freedom.)

Before doing any work, I considered some pathological examples and mathematical properties I expected:
* The binary branching index <= total branching index, with equality only when *some hand-wavy "this should be simple to determine later"*
* A lexicon of 1 word would have a branching index of 0. (Every prefix would have only one option for the letter that could follow it, where we allow "" to be a letter.)
* As a lexicon became increasingly without constraint (e.g., every combination of letters forming a valid word), its branching index would tend toward 1.
* A logographic lexicon (one character per word) would have a binary branching index of 1/(cardinality(lexicon)+1) and a total branching index of (cardinality(lexicon)-1)/(cardinality(lexicon)+1). (+1 ensures we count initial "" as a valid prefix.)
* A lexicon consisting of "a," "aa," "aaa," "aaaa", ... (a+) would have a binary/total branching index of 1/(cardinality(lexicon)+1).
* The branching index is a measure of information: how much information does a given prefix give us about what words might follow? A higher branching index means that words are, in some sense, "closer together": we have less information about how to predict a word based on a given prefix. A lower branching index means that words are, in some sense, "sparser": we have moe information about how to predict a word based on a given prefix.
* The branching indices for a "uniformly randomly" (in quotes since this requires more explanation to be well-defined) constructed lexicon (given some alphabet) should be lower than the branching indices for a natural language lexicon since there are no morphological constraints on the random lexicon. In other words, we would expect more information from a prefix in a randomly generated language because the space should be sparser. (In English, we have "apply," "application," "applications", etc. In a "random" lexicon, it is unlikely we would have so many similar strings.)
