# `FAWOC` the FAst WOrd Classifier

FAWOC is a TUI program for manually labelling a list of words.
It has been developed to support the efficient clustering of documents based on topic modeling algorithms such as Dirichlet Latent Allocation.

![](screenshot-fawoc-edit.png)

The programs reads a CSV file containing the terms and allows the fast association of labels to the terms.

Each term is presented to the user, who can associate to the term one of the labels with the press of a key.

Some statistics are provided in the user interface to have a clue about the number of classified terms and the remaining ones.

The terms are sorted according to their frequency in the set of documents, which is a value that must be made available to FAWOC.

## Available commands and keybindings

* k keyword
* n noise
* r relevant
* x not-relevant
* p postponed
* a autonoise
* b barrier
* w save immediately
* q quit

## Logging

FAWOC writes profiling information into the file `profiler.log` with the relevant operations that are carried out.
