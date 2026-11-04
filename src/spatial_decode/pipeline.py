"""Functions that connect analysis inputs to computation."""

from spatial_decode.binning import bin_counts
from spatial_decode.config import load_config
from spatial_decode.dataset import load_dataset
from spatial_decode.deconvolve import deconvolve
from spatial_decode.estimate_cell_type_signatures import (
    cell_id_match,
    mean_expression_matrix,
    merge_counts_types,
)
from spatial_decode.spatialdomaindetection import (
    composition_to_grid,
    detect_domains,
    labels_to_frame,
)


def prepare_binned_counts(dataset_path, config_path):
    """Load analysis inputs and return spatial counts at the configured bin size."""
    config = load_config(config_path)
    dataset = load_dataset(dataset_path)

    return bin_counts(
        counts=dataset["counts"],
        coordinates=dataset["coordinates"],
        bin_size_um=config["bin_size_um"],
        square_size_um=dataset["metadata"]["square_size_um"],
    )


def _fractions_to_long(fractions, bin_ids):
    """Convert wide per-bin fractions to the contract's long composition table."""
    frame = fractions.copy()
    frame.insert(0, "bin_id", bin_ids.to_numpy())

    return frame.melt(
        id_vars="bin_id",
        var_name="cell_type",
        value_name="fraction",
    )


def run_analysis(dataset_path, config_path):
    """Run binning, deconvolution, and spatial-domain detection.

    Args:
        dataset_path: Directory containing a Data Contract-compatible dataset.
        config_path: YAML file containing analysis parameters.

    Returns:
        Dictionary containing binned transcript counts, the reference signature
        matrix, predicted cell-type composition, and smoothed and unsmoothed
        spatial-domain predictions.
    """
    config = load_config(config_path)
    dataset = load_dataset(dataset_path)

    # 1. Spatial binning
    binned_counts = bin_counts(
        counts=dataset["counts"],
        coordinates=dataset["coordinates"],
        bin_size_um=config["bin_size_um"],
        square_size_um=dataset["metadata"]["square_size_um"],
    )

    # 2. Estimate reference cell-type signatures
    reference_counts = dataset["reference_counts"]
    reference_labels = dataset["reference_labels"]

    if not cell_id_match(reference_counts, reference_labels):
        raise ValueError(
            "reference_counts and reference_labels contain different cell IDs"
        )

    merged_reference = merge_counts_types(
        reference_counts,
        reference_labels,
    )
    signatures = mean_expression_matrix(merged_reference)

    # 3. Deconvolution
    gene_columns = [
        column
        for column in binned_counts.columns
        if column not in {"bin_id", "bin_row", "bin_col"}
    ]

    fractions_wide = deconvolve(
        signatures,
        binned_counts[gene_columns],
    )

    predicted_composition = _fractions_to_long(
        fractions_wide,
        binned_counts["bin_id"],
    )

    # 4. Convert composition table to the regular spatial grid
    n_rows = int(binned_counts["bin_row"].max()) + 1
    n_cols = int(binned_counts["bin_col"].max()) + 1

    composition_grid, cell_types = composition_to_grid(
        predicted_composition,
        n_rows=n_rows,
        n_cols=n_cols,
    )

    # 5. Detect spatial domains
    labels_smoothed, labels_unsmoothed = detect_domains(
        composition_grid,
        n_domains=config["n_domains"],
        radius=config["smoothing_radius"],
        seed=config["seed"],
        n_init=config["kmeans_n_init"],
    )

    predicted_domains = labels_to_frame(labels_smoothed)
    predicted_domains_unsmoothed = labels_to_frame(labels_unsmoothed)

    return {
        "binned_counts": binned_counts,
        "signatures": signatures,
        "predicted_composition": predicted_composition,
        "predicted_domains": predicted_domains,
        "predicted_domains_unsmoothed": predicted_domains_unsmoothed,
        "cell_types": cell_types,
    }
