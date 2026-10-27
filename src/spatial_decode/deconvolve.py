from scipy.optimize import nnls


def deconvolve(S, binned_counts):
    """Estimate cell-type composition for each bin using non-negative least squares.

    For each bin, solves: minimise || y - S·w ||² subject to w ≥ 0,
    where y is the bin's count vector and w are the cell-type weights.
    S is column-normalised inside this function so that w / w.sum() gives
    transcript fractions, not cell fractions.

    Args:
        S: DataFrame of shape (n_genes, n_cell_types) — mean expression per
           cell type, as raw counts. Columns are normalised to sum to 1 here.
        binned_counts: DataFrame of shape (n_bins, n_genes) — transcript counts
                       per bin, genes as columns.

    Returns:
        List of length n_bins, each entry a numpy array of shape (n_cell_types,)
        with non-negative fractions summing to 1.
    """
    S_normalised = S / S.sum()
    fractions_per_bin = []
    for _, bin_vector in binned_counts.iterrows():
        weights, _ = nnls(S_normalised.values, bin_vector.values)
        fractions_per_bin.append(weights / weights.sum())
    return fractions_per_bin
