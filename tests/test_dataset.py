"""Tests for dataset loading."""

import json

from spatial_decode.dataset import load_dataset


def test_load_dataset_reads_expected_files(tmp_path):
    """Load all legitimate analysis inputs from a minimal dataset."""
    dataset_dir = tmp_path / "dataset"
    reference_dir = dataset_dir / "reference"
    reference_dir.mkdir(parents=True)

    metadata = {
        "contract_version": "1.0",
        "square_size_um": 2,
    }

    (dataset_dir / "metadata.json").write_text(json.dumps(metadata))

    (dataset_dir / "coordinates.csv").write_text(
        "square_id,array_row,array_col,x_um,y_um\nsq_r000_c000,0,0,1.0,1.0\n"
    )

    (dataset_dir / "counts.csv").write_text("square_id,GENE_0001\nsq_r000_c000,3\n")

    (reference_dir / "reference_counts.csv").write_text(
        "cell_id,GENE_0001\nref_0001,5\n"
    )

    (reference_dir / "reference_labels.csv").write_text(
        "cell_id,cell_type\nref_0001,A\n"
    )

    dataset = load_dataset(dataset_dir)

    assert set(dataset) == {
        "metadata",
        "coordinates",
        "counts",
        "reference_counts",
        "reference_labels",
    }

    assert dataset["metadata"]["contract_version"] == "1.0"

    assert dataset["coordinates"].shape == (1, 5)
    assert dataset["counts"].shape == (1, 2)
    assert dataset["reference_counts"].shape == (1, 2)
    assert dataset["reference_labels"].shape == (1, 2)

    assert dataset["counts"].loc[0, "GENE_0001"] == 3
    assert dataset["reference_labels"].loc[0, "cell_type"] == "A"
