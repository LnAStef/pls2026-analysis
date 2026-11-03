# In the program estimate_cell_type_signatures.py: two reference data sets are loaded one containing cell types of each reference cell and on the number of transcripts per gene of each reference cell. The two data sets are merged and matrix with the mean expression profile generated. In this test should be evaluated if the programm generates the mean expression matrix based on a small data set.


import pandas as pd
from pandas.testing import assert_frame_equal

from spatial_decode.estimate_cell_type_signatures import (
    cell_id_match,
    merge_counts_types,
    mean_expression_matrix,
)


def test_mean_expression_matrix():
        """Test mean gene expression by cell type on a small reference dataset.

    Creates matching count and label tables for four reference cells, checks
    that their cell IDs match, merges the tables, and verifies that
    ``mean_expression_matrix`` returns the expected mean expression values.
    The expected matrix has genes as rows and cell types as columns.
    """
    transcripts = pd.DataFrame({
        "cell_id": ["Cell1", "Cell2", "Cell3", "Cell4"],
        "Gene1": [12, 4, 0, 6],
        "Gene2": [0, 8, 2, 4],
    })

    labels = pd.DataFrame({
        "cell_id": ["Cell1", "Cell2", "Cell3", "Cell4"],
        "cell_type": ["TypeA", "TypeB", "TypeB", "TypeA"],
    })


    assert cell_id_match(transcripts, labels)  # Requires cell_id_match to return a bool.

    merged = merge_counts_types(transcripts, labels)
    actual = mean_expression_matrix(merged)
    expected = pd.DataFrame(
        {
            "TypeA": [9.0, 2.0],
            "TypeB": [2.0, 5.0],
        },
        index=["Gene1", "Gene2"],
    )
    expected.columns.name = "cell_type"

    assert_frame_equal(actual, expected)
