## Estimate cell-type signatures

# Functions to import reference_counts.csv and reference_labels.csv
import pandas as pd


def load_reference_counts(path_ref_counts):
    """ Load the reference count table from a CSV file.
    Args: 
        path_ref_counts: path to file
    Returns:
        Count table 
    """
    ref_counts = pd.read_csv(path_ref_counts)
    return ref_counts


def load_reference_labels(path_ref_labels):
    """ Load the reference cell-label table from a CSV file
    
    Args.: 
        path_ref_labels : path to file
    Returns:
       table with cell types 
        """
    ref_labels = pd.read_csv(path_ref_labels)
    return ref_labels


def cell_id_match(transcripts, labels):
    """Return whether both tables contain the same non-missing cell IDs.
    Args.: 
        transcripts: Count table
        Labels: table with cell types
    Returns: 
        Boolean: True if cell_id of both tables match and False if not
    """
    transcript_ids = set(
        transcripts["cell_id"].dropna().astype(str).str.strip()
    )
    label_ids = set(
        labels["cell_id"].dropna().astype(str).str.strip()
    )
    return transcript_ids == label_ids


# Function to merge the two data sets by cell_id


def merge_counts_types(ref_counts, ref_labels):
    """ Join counts with cell_type labels using cell_id
    Args.:
        ref_count: Counts table containing cell_id column
        ref_labels: Label table containing cell_id and cell_type columns
    Returns: 
        Inner_joined table containing counts and cell_types
        """
    merged = ref_counts.merge(ref_labels, on="cell_id", how="inner")
    return merged


# Function to generate the matrix S with genes as rows and cell types as columns
def mean_expression_matrix(merged):
    """ Calculate mean expression per cell type
    Args.:
        merged: table containing cell_type and numeric gene transcript columns
    Returns:
        Mean expression matrix indexed by gene, with one column per cell type.
    """
    S = merged.groupby("cell_type").mean(numeric_only=True).T
    return S


# Function to write results in csv


def write_matrix(S, results_path):
    """ Write a gene-by-cell-type matrix to a CSV file.
    Args.:
        S: Matrix to write, with genes as rows and cell types as columns. 
    Returns:
        None 
        Writes matrix to disc"""
    S.to_csv(results_path)
