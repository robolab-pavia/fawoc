# `FAWOC` the FAst WOrd Classifier

FAWOC is a TUI program for manually labelling a list of words.
It has been developed to support the efficient clustering of documents based on topic modeling algorithms such as Dirichlet Latent Allocation.

![](screenshot-fawoc-edit.png)

The programs reads a CSV file containing the terms and allows the fast association of labels to the terms.

Each term is presented to the user, who can associate to the term one of the labels with the press of a key.

Some statistics are provided in the user interface to have a clue about the number of classified terms and the remaining ones.

The terms are sorted according to their frequency in the set of documents, which is a value that must be made available to FAWOC.

## Example of usage

```
fawoc words.csv
```

The input file `terms.csv` needs to have at least one column with the header (first column) called `term`.

## Available commands and keybindings

The following labels are currently supported:

* k keyword
* n noise
* r relevant
* x not-relevant
* s stopword
* p postponed
* a autonoise

Other keys allow to save and quit:

* w save immediately
* q quit

FAWOC automatically saves the changes on closing.
Moreover, it autosaves the changes every 10 classified words.

## Logging

FAWOC writes profiling information into the file `profiler.log` with the relevant operations that are carried out.
