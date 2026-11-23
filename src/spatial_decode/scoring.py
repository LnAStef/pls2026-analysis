"""Score analysis predictions against simulation ground truth."""

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from sklearn.metrics import adjusted_rand_score



def _square_to_bin_mapping(coordinates, bin_size_um, square_size_um):
    """Map each input square to its analysis bin."""
    bins_per_side = bin_size_um / square_size_um

    if not bins_per_side.is_integer():
        raise ValueError("bin_size_um must be an integer multiple of square_size_um")

    k = int(bins_per_side)

    mapping = coordinates[["square_id", "array_row", "array_col"]].copy()

    mapping["bin_row"] = mapping["array_row"] // k
    mapping["bin_col"] = mapping["array_col"] // k

    mapping["bin_id"] = [
        f"bin_r{row}_c{col}"
        for row, col in zip(mapping["bin_row"], mapping["bin_col"], strict=True,)]
    
    print("mapping done:", mapping)

    return mapping



def aggregate_truth_composition(truth_composition, coordinates, bin_size_um, square_size_um):
    """Aggregate square-level true transcript counts into bin-level fractions.
    Returns:
        DataFrame indexed by bin_id with one fraction column per cell type.
        Empty bins are retained with NaN composition."""
    mapping = _square_to_bin_mapping(coordinates, bin_size_um, square_size_um)

    truth = truth_composition.merge(mapping[["square_id", "bin_id"]], on="square_id", how="right", validate="many_to_one")

    counts = truth.pivot_table(index="bin_id", columns="cell_type", values="n_transcripts", aggfunc="sum", fill_value=0)

    # Retain every bin represented in the coordinates.
    all_bins = mapping["bin_id"].drop_duplicates()

    counts = counts.reindex(index=all_bins, fill_value=0)

    totals = counts.sum(axis=1)

    # Initialize all bins as undefined.
    composition = pd.DataFrame(np.nan, index=counts.index, columns=counts.columns, dtype=float)

    # Normalize only bins containing transcripts.
    non_empty = totals > 0

    composition.loc[non_empty] = counts.loc[non_empty].div(totals.loc[non_empty], axis=0)
    
    print("truth composition aggregated:", composition)

    return composition



def score_composition(predicted_composition, truth_composition, coordinates, bin_size_um, square_size_um):
    """Compute mean per-bin RMSE and Jensen-Shannon divergence.
    Also returns the ground-truth composition matrix.
    """
    truth = aggregate_truth_composition(truth_composition, coordinates, bin_size_um, square_size_um)

    predicted = predicted_composition.pivot(index="bin_id", columns="cell_type", values="fraction")

    # Only evaluate bins with defined ground-truth composition.
    common_bins = truth.index[truth.notna().any(axis=1)].intersection(predicted.index)

    if common_bins.empty:
        raise ValueError("predicted composition and ground truth contain no common "
            "non-empty bins")

    cell_types = sorted(set(truth.columns).union(predicted.columns))

    truth = truth.reindex(index=common_bins, columns=cell_types, fill_value=0.0)

    predicted = predicted.reindex(index=common_bins, columns=cell_types, fill_value=0.0)

    if predicted.isna().any(axis=None):
        raise ValueError("predicted composition contains undefined fractions "
            "for a non-empty truth bin")

    if (predicted < 0).any(axis=None):
        raise ValueError("predicted fractions must be non-negative")

    if not np.allclose(
        predicted.sum(axis=1).to_numpy(), 1.0, atol=1e-3):
        raise ValueError("predicted fractions must sum to 1 within each bin")

    squared_error = (predicted - truth) ** 2

    rmse_per_bin = np.sqrt(squared_error.mean(axis=1))

    js_per_bin = pd.Series([jensenshannon(predicted.loc[bin_id].to_numpy(), truth.loc[bin_id].to_numpy(), base=2,) ** 2
            for bin_id in common_bins], index=common_bins)

    return {"rmse": float(rmse_per_bin.mean()),
            "jensen_shannon_divergence": float(js_per_bin.mean()),
           "composition_matrix": aggregate_truth_composition(truth_composition, coordinates, bin_size_um, square_size_um)}


def score_domains(predicted_domains, truth_domains,coordinates, bin_size_um, square_size_um):
    """Compute square-level ARI for predicted spatial domains."""
    mapping = _square_to_bin_mapping(coordinates, bin_size_um, square_size_um)

    predicted_per_square = mapping[["square_id", "bin_id"]].merge(predicted_domains, on="bin_id", how="left", validate="many_to_one")

    comparison = predicted_per_square.merge(truth_domains, on="square_id", how="inner", suffixes=("_predicted", "_truth"), validate="one_to_one")

    if comparison["domain_predicted"].isna().any():
        raise ValueError("one or more squares have no predicted domain")

    print("domains were scored")
    
    return float(adjusted_rand_score(comparison["domain_truth"], comparison["domain_predicted"]))


def score(predicted_composition, predicted_domains, truth_composition, truth_domains, coordinates, bin_size_um, square_size_um,):
    """Return the Data Contract scoring metrics for one analysis run."""
    composition_scores = score_composition(predicted_composition, truth_composition, coordinates, bin_size_um, square_size_um)

    ari = score_domains(predicted_domains, truth_domains, coordinates, bin_size_um, square_size_um)

    return {**composition_scores, "ari": ari}
