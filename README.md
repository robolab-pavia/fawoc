# Support material for the FAST SLR workflow

The workflow is based on the following stages:

- selection of bibliographic data set (manual)
- extraction of n-grams (automatic)
- classification of n-grams (manual)
- clustering of documents (automatic)
- validation of the topics associated with the clusters (manual)
- derivation of statistics (automatic)

# FA.WO.C. comments

## TODO and possible features

- NEW FEATURE: the program should be able to open a list of strings coming from the source abstracts that contain the word under exaxmination, to help understanding its relevance; this could be done only upon user request - if too computational heavy - or always in real-time - if not so heavy.
- Allow the user to configure the keys associated to the different actions/class; a simple JSON file may contain the association "key <-> action".

# Possible efficient workflow to use FA.WO.C.

## Manual workflow

- stage 1: mark words either being NOISE or postponed (look for trivial noise words, such as "however, thus, require, ...")
- stage 2: classify the postponed words as either NOISE or RELEVANT
- stage 3: classify the relevant words as keywords or not

In all the stages, mark NOT-RELEVANT words if needed.

## Possible automatic stages

- probably stage 1 could be made automatic

# Available scripts and programs

The following scripts and programs are currently available. They are listed in the order that they are expected to be used in the SLR workflow.
All the scripts expect utf-8 files as input.

## `ris2csv.py`

- ACTION: Converts a file from the RIS to the CSV format.
- INPUT: RIS bibliographic file.
- OUTPUT: CSV file format with the desired columns.

The output is sent to stdout unless an output file name is explicitly specified.

The advice is to always start from the RIS format (instead of CSV or BIB) since it allows a better, easier and clearer separation among the different elements of a bibliographic item.
The command line parameters allow to select the fields to export fro the RIS file.

During the conversion, an unique progressive number is added to each paper, which acts as unique identifier in the rest of the processing (within a column named `id`).
Therefore, be careful to not mix different versions of the source RIS that may generate a different numbering of the papers.

TODO: add an option to append the output to an existing CSV file?

### Example of usage

The standard slr-kit workflow needs a CSV file with two columns: `title` and `abstract`. Such CSV file can be obtained with the command:

```
ris2csv --columns title,abstract dataset.ris > dataset_abstracts.csv
```

## `acronyms.py`

- ACTION: Extracts a list of acronyms from the abstracts.
- INPUT: CSV file with the list of abstracts generated by `ris2csv.py`.
- OUTPUT: CSV file containing the short and extended acronyms.

Uses the algorithm presented in A. Schwartz and M. Hearst, "A Simple Algorithm for Identifying Abbreviations Definitions in Biomedical Text", Biocomputing, 2003.

The script assumes that the abstracts are contained in a column named `abstract`. Therefore, if the input CSV comes from other sources (e.g., the direct export from online services), make sure that the `abstract` column is present in the CSV. It also require a column named `id`.

## `preprocess.py`

- ACTION: Performs the preprocessing of the abstract to prepare it for further processing.
- INPUT: The CSV file produced by `ris2csv.py`.
- OUTPUT: A CSV file containing the same columns of the input file, plus a new column `abstract_lem` containing the preprocessed abstract.

The preprocessing includes:

- Remove punctuations
- Convert to lowercase
- Remove tags
- Remove special characters and digits
- Stemming
- Lemmatisation

### Example of usage

The following example processes the `dataset_abstracts.csv` file and produces `dataset_preproc.csv`, which contains the same columns of the input file plus the `abstract_lem` column:

```
preprocess.py --stop-words stop_words.txt dataset_abstracts.csv > dataset_preproc.csv
```

## `gen-n-grams.py`

- ACTION: Extracts the terms ({1,2,3,4}-grams) from the abstracts.
- INPUT: The CSV file produced by `preprocess.py` (it works on the column `abstract_lem`).
- OUTPUT: A CSV file containing the list of terms and their frequency.

TODO: change name in `gen-terms.py`?

### Example of usage

Extracts terms from `dataset_preproc.csv` and store them in `dataset_terms.csv`:

```
gen-n-grams.py dataset_preproc.csv > dataset_terms.csv
```

## `fawoc.py`, the FAst WOrd Classifier

- ACTION: GUI program for the fast classification of terms.
- INPUT: The CSV file with the terms produced by `gen-n-grams.py`.
- OUTPUT: The same input CSV with the labels assigned to the terms.

NOTE: the program changes the content of the input file.

The program also writes profiling information into the file `profiler.log` with the relevant operations that are carried out.

TODO: if fawoc does not find the necessary "helper" columns in the input file, it must create them as empty columns

## `occurrences.py`

- ACTION: Determines the occurrences of the terms in the abstracts.
- INPUT: Two files: 1) the list of abstracts generated by `preprocess.py` and 2) the list of terms generated by `fawoc.py`
- OUTPUT: A JSON data structure with the position of every term in each abstract; the output is written to stdout by default.

### Example of usage

Extracts the occurrences of the terms listed in `dataset_terms.csv` in the abstracts contained in `dataset_preproc.csv`, storing the results in `dataset_occ_keyword.json`:

```
occurrences.py -l keyword dataset_preproc.csv dataset_terms.csv > dataset_occ_keyword.json
```

## `dtm.py`

- ACTION: Calculates the document-terms matrix
- INPUT: The terms-documents JSON produced by `occurrences.py`
- OUTPUT: A CSV file containing the matrix; terms are on the rows, documents IDs are on the columns

Document IDs match with the ones assigned by `ris2csv.py`.

### Example of usage

Calculates the document-terms matrix starting from `dataset_occ_keyword.json` and storing the matrix in `dataset_dtm.csv`:

```
dtm.py dataset_occ_keyword.json > dataset_dtm.csv
```

## `cosine_similarity.py`

- ACTION: Calculates the cosine similarity of the document-terms matrix (generated by `dtm.py`)
- INPUT: CSV file with document-terms matrix
- OUTPUT: CSV file with the cosine similarity of terms

### Example of usage

```
cosine_similarity.py dataset_dtm.csv > dataset_cosine_similarity.csv
```

# Additional scripts

## `analyze-occ.py`

- ACTION: Generates the report of which document (abstract) contains which terms; for each document, reports all the contained terms, and the count.
- INPUT: The JSON file produced by `occurrences.py`.
- OUTPUT: A CSV file containing the list of documents (abstracts) containing the terms and the corresponding information.

## `noise-stats.py`

- ACTION: Calculate a statistic regarding noise words; it calculates, for each word, the ratio of the words labelled as noise (plus unlabelled words) against the total number of that word
- INPUT: The CSV file with the terms extracted by `gen-n-grams.py`.
- OUTPUT: A CSV files with one word (not a term!) per row, with its total count, number of noise labels and unlabelled items, plus the calculation of an index of noisiness

Notice that a word is not a term. In the term `this term important` there are the three words `this`, `term` and `important`.
This statistic could help to spot wrong labelling and/or words that are likely to be noise across several datasets.

It is an utility program that may not directly enter the main workflow, but can start providing interesting insights regarding noise words that can help, in the future, to spot possible noise words earlier, or to spot possible errors in the classification.


## `clear-postponed.py`

- ACTION: Removes the label `postponed` from the input file.
- INPUT: The CSV file with the terms extracted by `gen-n-grams.py`.
- OUTPUT: The same input file without the `postponed`.

TODO: being able to specify on the command line the label to remove.

## `cmp-terms.py`

- ACTION: Compare two CSV containing the same list of terms with possibly different labelling
- INPUT: The two CSV files in the format produced by `gen-n-grams.py`; they should containg the same list of terms
- OUTPUT: The list of terms that have different labels in the two files

## `copy-labels.py`

- ACTION: Copy the labels from the terms in the input CSV to the corresponding terms in the destination CSV.
- INPUT: The two CSV files in the format produced by `gen-n-grams.py`.
- OUTPUT: The list of terms in the destination CSV with labels assigned as in the input CSV.

This script is useful when doing experiments with subsets of a list of terms that was already labelled.
This type of experiments are indicated to save processing time during the development of scripts and algorithms.

## `gen-td-idf.py`

- ACTION: Calculates the TD-IDF index for the terms contained in the abstracts
- INPUT: The list of abstracts generated by `preprocess.py`
- OUTPUT: CSV containing the words with the top index

NOTE: At the moment, this script works on the complete lemmatized abstracts. It could be made better to work on the JSON output of `occurrences.py`.

## `match-occ-counts.py`

- ACTION: Serve per generare il file di report con keyword + not-relevant per ciascun articolo in modo da studiarne il comportamento
- INPUT:
- OUTPUT:

