"""Functions for loading spatial-decode datasets."""

import json
from pathlib import Path

import pandas as pd


def load_dataset(dataset_path):
    """Load the analysis inputs from a dataset directory."""
    dataset_path = Path(dataset_path).expanduser()

    metadata_path = dataset_path / "metadata.json"
    coordinates_path = dataset_path / "coordinates.csv"
    counts_path = dataset_path / "counts.csv"

    reference_path = dataset_path / "reference"
    reference_counts_path = reference_path / "reference_counts.csv"
    reference_labels_path = reference_path / "reference_labels.csv"

    metadata = json.loads(metadata_path.read_text())
    coordinates = pd.read_csv(coordinates_path)
    counts = pd.read_csv(counts_path)
    reference_counts = pd.read_csv(reference_counts_path)
    reference_labels = pd.read_csv(reference_labels_path)

    return {
        "metadata": metadata,
        "coordinates": coordinates,
        "counts": counts,
        "reference_counts": reference_counts,
        "reference_labels": reference_labels,
    }
