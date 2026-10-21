"""Tests for spatial binning."""

import pandas as pd

from spatial_decode.binning import bin_counts


def test_bin_counts_sums_squares_exactly():
    """Four 2 um squares should sum exactly into one 4 um bin."""
    coordinates = pd.DataFrame(
        {
            "square_id": [
                "sq_r000_c000",
                "sq_r000_c001",
                "sq_r001_c000",
                "sq_r001_c001",
            ],
            "array_row": [0, 0, 1, 1],
            "array_col": [0, 1, 0, 1],
        }
    )

    counts = pd.DataFrame(
        {
            "square_id": [
                "sq_r000_c000",
                "sq_r000_c001",
                "sq_r001_c000",
                "sq_r001_c001",
            ],
            "GENE_0001": [1, 2, 3, 4],
            "GENE_0002": [10, 20, 30, 40],
        }
    )

    result = bin_counts(
        counts=counts,
        coordinates=coordinates,
        bin_size_um=4,
        square_size_um=2,
    )

    assert len(result) == 1
    assert result.loc[0, "bin_id"] == "bin_r0_c0"
    assert result.loc[0, "GENE_0001"] == 10
    assert result.loc[0, "GENE_0002"] == 100

def test_four_8um_bins_sum_to_one_16um_bin():
    """Four 8 um bins should sum exactly to the matching 16 um bin."""
    square_size_um = 2

    square_ids = []
    array_rows = []
    array_cols = []
    gene_1 = []
    gene_2 = []

    for row in range(8):
        for col in range(8):
            square_ids.append(f"sq_r{row:03d}_c{col:03d}")
            array_rows.append(row)
            array_cols.append(col)

            gene_1.append(1)
            gene_2.append(row + col)

    coordinates = pd.DataFrame(
        {
            "square_id": square_ids,
            "array_row": array_rows,
            "array_col": array_cols,
        }
    )

    counts = pd.DataFrame(
        {
            "square_id": square_ids,
            "GENE_0001": gene_1,
            "GENE_0002": gene_2,
        }
    )

    bins_8um = bin_counts(
        counts=counts,
        coordinates=coordinates,
        bin_size_um=8,
        square_size_um=square_size_um,
    )

    bins_16um = bin_counts(
        counts=counts,
        coordinates=coordinates,
        bin_size_um=16,
        square_size_um=square_size_um,
    )

    assert len(bins_8um) == 4
    assert len(bins_16um) == 1

    assert bins_16um.loc[0, "GENE_0001"] == bins_8um["GENE_0001"].sum()
    assert bins_16um.loc[0, "GENE_0002"] == bins_8um["GENE_0002"].sum()

