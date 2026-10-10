"""Tests for loading contract-conforming analysis inputs."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from spatial_decode.io import load_dataset


def _write_tiny_dataset(root: Path) -> Path:
    """Create a four-square, two-gene dataset."""
    root.mkdir()

    metadata = {
        "contract_version": "1.0",
        "square_size_um": 2.0,
        "grid": {
            "n_rows": 2,
            "n_cols": 2,
        },
        "field_um": {
            "width": 4.0,
            "height": 4.0,
        },
        "n_squares": 4,
        "n_genes": 2,
        "cell_types": ["A", "B"],
        "created_utc": "2026-01-01T00:00:00Z",
        "generator": {
            "name": "test",
            "version": "0",
            "git_commit": "test",
        },
        "random_seed": 1,
    }

    (root / "metadata.json").write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )

    (root / "coordinates.csv").write_text(
        "square_id,array_row,array_col,x_um,y_um\n"
        "sq_r000_c000,0,0,1.0,1.0\n"
        "sq_r000_c001,0,1,3.0,1.0\n"
        "sq_r001_c000,1,0,1.0,3.0\n"
        "sq_r001_c001,1,1,3.0,3.0\n",
        encoding="utf-8",
    )

    (root / "counts.csv").write_text(
        "square_id,g1,g2\n"
        "sq_r000_c000,1,0\n"
        "sq_r000_c001,0,2\n"
        "sq_r001_c000,3,1\n"
        "sq_r001_c001,0,4\n",
        encoding="utf-8",
    )

    reference_dir = root / "reference"
    reference_dir.mkdir()

    (reference_dir / "reference_counts.csv").write_text(
        "cell_id,g1,g2\nref_0001,4,1\nref_0002,5,1\nref_0003,1,4\nref_0004,1,5\n",
        encoding="utf-8",
    )

    (reference_dir / "reference_labels.csv").write_text(
        "cell_id,cell_type\nref_0001,A\nref_0002,A\nref_0003,B\nref_0004,B\n",
        encoding="utf-8",
    )

    return root


def test_load_dataset_reports_expected_shapes_and_gene_order(
    tmp_path: Path,
) -> None:
    root = _write_tiny_dataset(tmp_path / "dataset")

    dataset = load_dataset(root)

    assert dataset.spatial_shape == (4, 2)
    assert dataset.reference_shape == (4, 2)
    assert dataset.gene_ids == ["g1", "g2"]
    assert dataset.metadata["contract_version"] == "1.0"


def test_load_dataset_does_not_read_ground_truth(
    tmp_path: Path,
) -> None:
    root = _write_tiny_dataset(tmp_path / "dataset")

    ground_truth = root / "ground_truth"
    ground_truth.mkdir()

    (ground_truth / "params.json").write_text(
        "deliberately invalid JSON",
        encoding="utf-8",
    )

    dataset = load_dataset(root)

    assert dataset.spatial_shape == (4, 2)


def test_load_dataset_aligns_reference_labels_by_cell_id(
    tmp_path: Path,
) -> None:
    root = _write_tiny_dataset(tmp_path / "dataset")

    labels_path = root / "reference" / "reference_labels.csv"

    labels_path.write_text(
        "cell_id,cell_type\nref_0004,B\nref_0002,A\nref_0001,A\nref_0003,B\n",
        encoding="utf-8",
    )

    dataset = load_dataset(root)

    assert dataset.reference_labels["cell_id"].tolist() == [
        "ref_0001",
        "ref_0002",
        "ref_0003",
        "ref_0004",
    ]


def test_load_dataset_rejects_unsupported_contract_version(
    tmp_path: Path,
) -> None:
    root = _write_tiny_dataset(tmp_path / "dataset")

    metadata_path = root / "metadata.json"

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    metadata["contract_version"] = "2.0"

    metadata_path.write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported contract_version",
    ):
        load_dataset(root)


def test_load_dataset_rejects_negative_counts(
    tmp_path: Path,
) -> None:
    root = _write_tiny_dataset(tmp_path / "dataset")

    counts_path = root / "counts.csv"

    counts_path.write_text(
        counts_path.read_text(encoding="utf-8").replace(
            "sq_r000_c000,1,0",
            "sq_r000_c000,-1,0",
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="negative count",
    ):
        load_dataset(root)


def test_load_dataset_rejects_reference_gene_order_mismatch(
    tmp_path: Path,
) -> None:
    root = _write_tiny_dataset(tmp_path / "dataset")

    reference_path = root / "reference" / "reference_counts.csv"

    reference_path.write_text(
        reference_path.read_text(encoding="utf-8").replace(
            "cell_id,g1,g2",
            "cell_id,g2,g1",
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="gene columns must match",
    ):
        load_dataset(root)


def test_load_dataset_rejects_square_id_mismatch(
    tmp_path: Path,
) -> None:
    root = _write_tiny_dataset(tmp_path / "dataset")

    counts_path = root / "counts.csv"

    counts_path.write_text(
        counts_path.read_text(encoding="utf-8").replace(
            "sq_r001_c001,0,4",
            "wrong_square,0,4",
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="square_id values must match",
    ):
        load_dataset(root)
