"""Functions for loading spatial-decode datasets."""

import json
from pathlib import Path

import pandas as pd


def load_dataset(path):
    """Load the legitimate analysis inputs from a dataset directory."""
    path = Path(path)

    metadata = json.loads((path / "metadata.json").read_text())

    coordinates = pd.read_csv(path / "coordinates.csv")

    counts = pd.read_csv(path / "counts.csv")

    reference_counts = pd.read_csv(path / "reference" / "reference_counts.csv")

    reference_labels = pd.read_csv(path / "reference" / "reference_labels.csv")

    return {
        "metadata": metadata,
        "coordinates": coordinates,
        "counts": counts,
        "reference_counts": reference_counts,
        "reference_labels": reference_labels,
    }
