import numpy as np
import pandas as pd
from scipy.optimize import nnls


def normalise_columns(S):
    """Scale each column of S to sum to 1.

    Args:
        S: DataFrame (genes x cell types) of mean reference counts per cell type.

    Returns:
        DataFrame of the same shape. Each column is a relative expression
        profile: the proportion of that cell type's transcripts coming from
        each gene (no unit).

    >>> S = pd.DataFrame({"A": [8.0, 2.0], "B": [1.0, 3.0]}, index=["g1", "g2"])
    >>> normalise_columns(S)["A"].tolist()
    [0.8, 0.2]
    >>> normalise_columns(S)["B"].tolist()
    [0.25, 0.75]
    """
    return S / S.sum()


def to_fractions(weights):
    """Convert one bin's transcript weights into fractions of that bin's transcripts.

    Args:
        weights: 1-D array of estimated transcripts per cell type for ONE bin
            (the analyzer's estimate, from the NNLS solve).

    Returns:
        1-D array of fractions summing to 1. If the weights sum to zero the
        composition is undefined, so every entry is NaN.

    >>> to_fractions(np.array([30.0, 10.0, 0.0])).tolist()
    [0.75, 0.25, 0.0]
    >>> to_fractions(np.zeros(3)).tolist()
    [nan, nan, nan]
    """
    total = weights.sum()
    if total == 0:
        return np.full(weights.shape, np.nan)
    return weights / total


def deconvolve(S, binned_counts):
    """Estimate the cell-type composition of each bin with non-negative least squares.

    Args:
        S: DataFrame (genes x cell types), mean reference counts per type.
            Index = gene names, columns = cell-type names.
        binned_counts: DataFrame (bins x genes), transcript counts. Columns
            must be the same gene names as S.index, in any order.

    Returns:
        DataFrame (bins x cell types) of estimated transcript fractions.
        Rows sum to 1, except bins with zero transcripts, which are NaN.

    Raises:
        ValueError: if the gene names of S and binned_counts differ.
    """
    if set(S.index) != set(binned_counts.columns):
        raise ValueError("gene names of S and binned_counts do not match")

    counts = binned_counts.loc[:, S.index]
    S_normalised = normalise_columns(S)

    fractions = np.full((len(counts), S.shape[1]), np.nan)
    for i, (_, bin_vector) in enumerate(counts.iterrows()):
        weights, _ = nnls(S_normalised.to_numpy(), bin_vector.to_numpy(dtype=float))
        fractions[i] = to_fractions(weights)
    return pd.DataFrame(fractions, index=counts.index, columns=S.columns)