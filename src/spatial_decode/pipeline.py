"""Functions that connect analysis inputs to computation."""

from spatial_decode.binning import bin_counts
from spatial_decode.config import load_config
from spatial_decode.dataset import load_dataset


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
