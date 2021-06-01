# `FAWOC` the FAst WOrd Classifier

FAWOC is a TUI program for manually labelling a list of words.
It has been developed to support the efficient clustering of documents based on topic modeling algorithms such as Dirichlet Latent Allocation.

![](screenshot-fawoc-edit.png)

The programs reads a CSV file containing the terms and allows the fast association of labels to the terms.

NOTE: the program changes the content of the input file.

The program uses also two files to save its state and retrieve some information about terms.
Assuming that the input file is called `dataset_terms.tsv`, FAWOC uses `dataset_terms_fawoc_data.json` and `dataset_terms_fawoc_data.tsv`.
This two files are searched and saved in the same directory of the input file.
The json file is used to save the state of FAWOC, and it is saved every time the input file is updated.
The tsv file is used to load some additional data about the terms (currently only the terms count).
This file is not modified by FAWOC.
If these two file are not present, they are created by FAWOC, the json file with the current state.
The tsv file is created with data eventually loaded from the input file.
If no count field was present in the input file a default value of -1 is used for all terms.

FAWOC saves data every 10 classsifications.
To save data more often, use the 'w' key.

The program also writes profiling information into the file `profiler.log` with the relevant operations that are carried out.
