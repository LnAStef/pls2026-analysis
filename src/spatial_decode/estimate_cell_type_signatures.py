## Estimate cell-type signatures

# Functions to import reference_counts.csv and reference_labels.csv
import pandas as pd

def load_reference_counts(path_ref_counts):
    ref_counts = pd.read_csv(path_ref_counts)
    return ref_counts
    
def load_reference_labels(path_ref_labels):
    ref_labels = pd.read_csv(path_ref_labels)
    return ref_labels



# Function to check if all the reference cells are in both csv files
def cell_id_match(rname, transcripts, labels):
    match = set(transcripts["rname"].dropna().astype(str).str.strip()) == \
            set(labels["rname"].dropna().astype(str).str.strip())
    return print(match)



# Function to merge the two data sets by cell_id 

def merge_counts_types(ref_counts, ref_labels):
    merged = ref_counts.merge(ref_labels, on="cell_id", how="inner")
    return merged
    
# Function to generate the matrix S with genes as rows and cell types as columns
def mean_expression_matrix(merged):
    S = merged.groupby("cell_type").mean(numeric_only=True).T
    return S


# Function to write results in csv

def write_matrix(S, results_path):
    S.to_csv(results_path)