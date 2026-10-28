"""Spatial-domain detection (spec §3.4): smooth the per-bin compositions, then cluster.

Compositions live on a regular grid of bins, shape (n_rows, n_cols, n_types). A bin that
holds no transcripts has no defined composition and is represented by NaN in all its
entries; every function here treats such bins as "missing", never as zeros.
"""

import numpy as np
import pandas as pd
from scipy.ndimage import uniform_filter
from sklearn.cluster import KMeans

UNASSIGNED = -1  # label for bins that have no composition at all, even after smoothing


def _valid_mask(comp):
    """Boolean (n_rows, n_cols) mask: True where a bin has a defined composition."""
    return ~np.isnan(comp).any(axis=-1)


def smooth_composition(comp, radius):
    """Average each bin's composition over itself and its neighbours.

    The window is (2*radius+1) x (2*radius+1) bins. Two edge cases are handled on purpose:

    * Grid border: the window is cut off, and only the bins that exist are averaged
      (no padding with zeros or mirrored values).
    * Empty bins (NaN): they are left out of the average, so they neither pull
      neighbours towards zero nor count in the divisor. An empty bin itself gets the
      average of its valid neighbours; if it has none, it stays NaN.

    Because each valid input vector sums to 1 and every valid bin in the window has the
    same weight, every output vector also sums to 1 and is non-negative.

    Args:
        comp: float array (n_rows, n_cols, n_types) of per-bin fractions; NaN rows = empty.
        radius: window half-width in bins, >= 0. 0 returns an unchanged copy.
    Returns:
        float array of the same shape as `comp`.
    """
    comp = np.asarray(comp, dtype=float)
    if comp.ndim != 3:
        raise ValueError(
            f"comp must have shape (n_rows, n_cols, n_types), got {comp.shape}"
        )
    if radius < 0 or int(radius) != radius:
        raise ValueError(f"radius must be a non-negative integer, got {radius}")
    if radius == 0:
        return comp.copy()

    valid = _valid_mask(comp)
    filled = np.where(valid[..., None], comp, 0.0)
    size = (
        2 * int(radius) + 1,
        2 * int(radius) + 1,
        1,
    )  # no smoothing across cell types

    # uniform_filter returns window means; the ratio of two means equals sum / n_valid.
    # mode="constant" with cval=0 makes outside-the-grid positions count as "not valid".
    mean_values = uniform_filter(filled, size=size, mode="constant", cval=0.0)
    mean_valid = uniform_filter(
        valid.astype(float), size=size[:2], mode="constant", cval=0.0
    )

    smoothed = np.full(comp.shape, np.nan)
    has_neighbours = mean_valid > 1e-12  # float-safe test for "at least one valid bin"
    smoothed[has_neighbours] = (
        mean_values[has_neighbours] / mean_valid[has_neighbours][:, None]
    )
    return smoothed


def cluster_domains(comp, n_domains, seed, n_init):
    """Cluster bins into spatial domains with KMeans on their composition vectors.

    KMeans is fitted only on bins with a defined composition. Bins without one get
    `UNASSIGNED` (-1). Label numbers are arbitrary (permuting them changes nothing for ARI).

    Args:
        comp: float array (n_rows, n_cols, n_types); NaN rows = no composition.
        n_domains: K, number of clusters.
        seed: random_state of KMeans (reproducibility, E8).
        n_init: number of KMeans restarts.
    Returns:
        int array (n_rows, n_cols) of domain labels.
    """
    comp = np.asarray(comp, dtype=float)
    valid = _valid_mask(comp)
    if valid.sum() < n_domains:
        raise ValueError(
            f"need at least n_domains={n_domains} bins with a composition, got {valid.sum()}"
        )
    model = KMeans(n_clusters=n_domains, random_state=seed, n_init=n_init)
    labels = np.full(comp.shape[:2], UNASSIGNED, dtype=int)
    labels[valid] = model.fit_predict(comp[valid])
    return labels


def detect_domains(comp, n_domains, radius, seed, n_init):
    """Run domain detection with and without spatial smoothing (the spec asks for both).

    Args:
        comp: float array (n_rows, n_cols, n_types) of per-bin fractions from §3.3.
        n_domains: K, number of clusters.
        radius: smoothing half-width in bins; see `smooth_composition`.
        seed: KMeans random_state.
        n_init: number of KMeans restarts.
    Returns:
        (labels_smoothed, labels_unsmoothed): two int arrays (n_rows, n_cols).
    """
    labels_smoothed = cluster_domains(
        smooth_composition(comp, radius), n_domains, seed, n_init
    )
    labels_unsmoothed = cluster_domains(comp, n_domains, seed, n_init)
    return labels_smoothed, labels_unsmoothed


def composition_to_grid(frame, n_rows, n_cols):
    """Turn the long table (bin_id, cell_type, fraction) into a (n_rows, n_cols, n_types) grid.

    Bins that do not appear in the table come out as NaN (= empty). Cell types are
    ordered alphabetically, which fixes the order of the last axis.

    Args:
        frame: DataFrame with columns bin_id ('bin_r<row>_c<col>'), cell_type, fraction.
        n_rows, n_cols: size of the bin grid.
    Returns:
        (grid, cell_types): float array and the list of cell types along its last axis.
    """
    parts = frame["bin_id"].str.extract(r"^bin_r(\d+)_c(\d+)$").astype(int)
    if parts.isna().any(axis=None):
        raise ValueError("bin_id values must look like 'bin_r<row>_c<col>'")
    cell_types = sorted(frame["cell_type"].unique())
    type_idx = (
        frame["cell_type"].map({t: i for i, t in enumerate(cell_types)}).to_numpy()
    )
    grid = np.full((n_rows, n_cols, len(cell_types)), np.nan)
    grid[parts[0].to_numpy(), parts[1].to_numpy(), type_idx] = frame[
        "fraction"
    ].to_numpy()
    # A bin listed with only some types is missing the others: they are zero, not unknown.
    listed = ~np.isnan(grid).all(axis=-1)
    grid[listed] = np.nan_to_num(grid[listed], nan=0.0)
    return grid, cell_types


def labels_to_frame(labels):
    """Format a label grid as the contract's predicted_domains.csv (columns bin_id, domain).

    Args:
        labels: int array (n_rows, n_cols).
    Returns:
        DataFrame with one row per bin, ids 'bin_r<row>_c<col>'.
    """
    rows, cols = np.indices(labels.shape)
    return pd.DataFrame(
        {
            "bin_id": [
                f"bin_r{r}_c{c}"
                for r, c in zip(rows.ravel(), cols.ravel(), strict=True)
            ],
            "domain": labels.ravel(),
        }
    )
