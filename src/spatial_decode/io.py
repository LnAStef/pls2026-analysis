"""Load spatial transcriptomics datasets that follow Data Contract 1.0."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

SUPPORTED_CONTRACT_VERSION = "1.0"


@dataclass(frozen=True)
class SpatialDataset:
    """Legitimate analysis inputs loaded from one dataset directory."""

    root: Path
    metadata: dict[str, Any]
    coordinates: pd.DataFrame
    counts: pd.DataFrame
    reference_counts: pd.DataFrame
    reference_labels: pd.DataFrame

    @property
    def gene_ids(self) -> list[str]:
        """Return the gene identifiers in their stored order."""
        return list(self.counts.columns[1:])

    @property
    def spatial_shape(self) -> tuple[int, int]:
        """Return ``(number of squares, number of genes)``."""
        return len(self.counts), len(self.gene_ids)

    @property
    def reference_shape(self) -> tuple[int, int]:
        """Return ``(number of reference cells, number of genes)``."""
        return len(self.reference_counts), len(self.gene_ids)


def load_dataset(dataset_dir: str | Path) -> SpatialDataset:
    """Load legitimate inputs and apply early sanity checks.

    The function deliberately does not read ``ground_truth/``. Ground truth is
    reserved for scoring and tests, not for inference.

    Args:
        dataset_dir: Directory containing ``metadata.json``, ``coordinates.csv``,
            ``counts.csv`` and the ``reference/`` directory.

    Returns:
        A dataset whose spatial and reference tables are aligned.

    Raises:
        FileNotFoundError: If the dataset directory or a required file is absent.
        ValueError: If the loaded inputs fail a sanity check.
    """
    root = Path(dataset_dir).expanduser().resolve()

    if not root.is_dir():
        raise FileNotFoundError(f"Dataset directory does not exist: {root}")

    paths = {
        "metadata.json": root / "metadata.json",
        "coordinates.csv": root / "coordinates.csv",
        "counts.csv": root / "counts.csv",
        "reference/reference_counts.csv": (root / "reference" / "reference_counts.csv"),
        "reference/reference_labels.csv": (root / "reference" / "reference_labels.csv"),
    }

    missing = [name for name, path in paths.items() if not path.is_file()]

    if missing:
        raise FileNotFoundError(
            "Missing required dataset file(s): " + ", ".join(missing)
        )

    try:
        metadata = json.loads(paths["metadata.json"].read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("metadata.json is not valid JSON") from exc

    if not isinstance(metadata, dict):
        raise ValueError("metadata.json must contain a JSON object")

    contract_version = metadata.get("contract_version")

    if contract_version != SUPPORTED_CONTRACT_VERSION:
        raise ValueError(
            f"Unsupported contract_version "
            f"{contract_version!r}; expected "
            f"{SUPPORTED_CONTRACT_VERSION!r}"
        )

    coordinates = pd.read_csv(paths["coordinates.csv"])
    counts = pd.read_csv(paths["counts.csv"])

    reference_counts = pd.read_csv(paths["reference/reference_counts.csv"])

    reference_labels = pd.read_csv(paths["reference/reference_labels.csv"])

    reference_labels = _validate_and_align_tables(
        metadata=metadata,
        coordinates=coordinates,
        counts=counts,
        reference_counts=reference_counts,
        reference_labels=reference_labels,
    )

    return SpatialDataset(
        root=root,
        metadata=metadata,
        coordinates=coordinates,
        counts=counts,
        reference_counts=reference_counts,
        reference_labels=reference_labels,
    )


def _validate_and_align_tables(
    *,
    metadata: dict[str, Any],
    coordinates: pd.DataFrame,
    counts: pd.DataFrame,
    reference_counts: pd.DataFrame,
    reference_labels: pd.DataFrame,
) -> pd.DataFrame:
    """Validate inexpensive invariants and align reference labels."""
    _require_columns(
        coordinates,
        [
            "square_id",
            "array_row",
            "array_col",
            "x_um",
            "y_um",
        ],
        "coordinates.csv",
    )

    _require_first_column(
        counts,
        "square_id",
        "counts.csv",
    )

    _require_first_column(
        reference_counts,
        "cell_id",
        "reference/reference_counts.csv",
    )

    _require_columns(
        reference_labels,
        ["cell_id", "cell_type"],
        "reference/reference_labels.csv",
    )

    _require_unique(
        coordinates["square_id"],
        "coordinates.csv square_id",
    )

    _require_unique(
        counts["square_id"],
        "counts.csv square_id",
    )

    _require_unique(
        reference_counts["cell_id"],
        "reference/reference_counts.csv cell_id",
    )

    _require_unique(
        reference_labels["cell_id"],
        "reference/reference_labels.csv cell_id",
    )

    if not coordinates["square_id"].equals(counts["square_id"]):
        raise ValueError(
            "coordinates.csv and counts.csv square_id "
            "values must match in the same order"
        )

    spatial_genes = list(counts.columns[1:])
    reference_genes = list(reference_counts.columns[1:])

    if not spatial_genes:
        raise ValueError("counts.csv must contain at least one gene column")

    if spatial_genes != reference_genes:
        raise ValueError(
            "Spatial and reference gene columns must match in the same order"
        )

    if metadata.get("n_squares") != len(counts):
        raise ValueError("metadata n_squares does not match the number of spatial rows")

    if metadata.get("n_genes") != len(spatial_genes):
        raise ValueError("metadata n_genes does not match the number of gene columns")

    _validate_count_values(
        counts,
        "counts.csv",
    )

    _validate_count_values(
        reference_counts,
        "reference/reference_counts.csv",
    )

    _validate_coordinates(
        coordinates,
        metadata,
    )

    count_ids = reference_counts["cell_id"]
    label_ids = reference_labels["cell_id"]

    if set(count_ids) != set(label_ids):
        raise ValueError(
            "Reference count and label files must contain the same cell_id values"
        )

    aligned_labels = reference_labels.set_index("cell_id").loc[count_ids].reset_index()

    declared_types = metadata.get("cell_types")

    if not isinstance(declared_types, list) or not all(
        isinstance(cell_type, str) for cell_type in declared_types
    ):
        raise ValueError("metadata cell_types must be a list of strings")

    if len(declared_types) != len(set(declared_types)):
        raise ValueError("metadata cell_types must not contain duplicates")

    if set(aligned_labels["cell_type"]) != set(declared_types):
        raise ValueError(
            "Reference labels must cover exactly the cell types in metadata"
        )

    return aligned_labels


def _require_columns(
    table: pd.DataFrame,
    required: list[str],
    filename: str,
) -> None:
    """Require named columns to be present."""
    missing = [column for column in required if column not in table.columns]

    if missing:
        raise ValueError(
            f"{filename} is missing required column(s): {', '.join(missing)}"
        )


def _require_first_column(
    table: pd.DataFrame,
    expected: str,
    filename: str,
) -> None:
    """Require the identifier column to be first."""
    if len(table.columns) == 0:
        raise ValueError(f"{filename} has no columns")

    if table.columns[0] != expected:
        raise ValueError(
            f"{filename} must start with {expected!r}, not {table.columns[0]!r}"
        )


def _require_unique(
    series: pd.Series,
    description: str,
) -> None:
    """Reject duplicated identifiers."""
    if series.duplicated().any():
        raise ValueError(f"{description} values must be unique")


def _validate_count_values(
    table: pd.DataFrame,
    filename: str,
) -> None:
    """Require gene values to be finite non-negative integers."""
    try:
        numeric = table.iloc[:, 1:].apply(
            pd.to_numeric,
            errors="raise",
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{filename} contains a non-numeric count") from exc

    values = numeric.to_numpy(dtype=float)

    if not np.isfinite(values).all():
        raise ValueError(f"{filename} contains a missing or infinite count")

    if (values < 0).any():
        raise ValueError(f"{filename} contains a negative count")

    if not np.equal(
        values,
        np.floor(values),
    ).all():
        raise ValueError(f"{filename} contains a non-integer count")


def _validate_coordinates(
    coordinates: pd.DataFrame,
    metadata: dict[str, Any],
) -> None:
    """Check grid indices and micrometre coordinates."""
    try:
        rows = pd.to_numeric(
            coordinates["array_row"],
            errors="raise",
        ).to_numpy(dtype=float)

        columns = pd.to_numeric(
            coordinates["array_col"],
            errors="raise",
        ).to_numpy(dtype=float)

        x_um = pd.to_numeric(
            coordinates["x_um"],
            errors="raise",
        ).to_numpy(dtype=float)

        y_um = pd.to_numeric(
            coordinates["y_um"],
            errors="raise",
        ).to_numpy(dtype=float)

        square_size_um = float(metadata["square_size_um"])

    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            "Grid coordinates and metadata square_size_um must be numeric"
        ) from exc

    for name, values in (
        ("array_row", rows),
        ("array_col", columns),
    ):
        if not np.isfinite(values).all():
            raise ValueError(f"{name} contains a missing or infinite value")

        if (values < 0).any() or not np.equal(
            values,
            np.floor(values),
        ).all():
            raise ValueError(f"{name} must contain non-negative integers")

    if square_size_um <= 0:
        raise ValueError("metadata square_size_um must be positive")

    if not np.isfinite(x_um).all() or not np.isfinite(y_um).all():
        raise ValueError("x_um and y_um must contain finite values")

    expected_x = (columns + 0.5) * square_size_um

    expected_y = (rows + 0.5) * square_size_um

    if not np.allclose(
        x_um,
        expected_x,
        rtol=0.0,
        atol=1e-9,
    ):
        raise ValueError("x_um is inconsistent with array_col and square_size_um")

    if not np.allclose(
        y_um,
        expected_y,
        rtol=0.0,
        atol=1e-9,
    ):
        raise ValueError("y_um is inconsistent with array_row and square_size_um")
