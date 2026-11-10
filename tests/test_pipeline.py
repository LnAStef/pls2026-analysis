import json

import pandas as pd

from spatial_decode.pipeline import prepare_binned_counts


def test_prepare_binned_counts_uses_config_and_metadata(tmp_path):
    """Use bin size from config and square size from dataset metadata."""
    dataset_path = tmp_path / "dataset"
    reference_path = dataset_path / "reference"
    ground_truth_path = dataset_path / "ground_truth"

    reference_path.mkdir(parents=True)
    ground_truth_path.mkdir()
    metadata = {
    "contract_version": "1.0",
    "square_size_um": 2,
    "grid": {
        "n_rows": 2,
        "n_cols": 2,
    },
    "cell_types": ["A"],
}
    (dataset_path / "metadata.json").write_text(json.dumps(metadata))

    coordinates = pd.DataFrame(
        {"square_id": ["s0", "s1", "s2", "s3"],
        "array_row": [0, 0, 1, 1],
        "array_col": [0, 1, 0, 1],
        "x_um": [1.0, 3.0, 1.0, 3.0],
        "y_um": [1.0, 1.0, 3.0, 3.0],
            }
    )
    coordinates.to_csv(dataset_path / "coordinates.csv", index=False)

    counts = pd.DataFrame(
        {
            "square_id": ["s0", "s1", "s2", "s3"],
            "GENE_1": [1, 2, 3, 4],
        }
    )
    counts.to_csv(dataset_path / "counts.csv", index=False)

    pd.DataFrame(
        {
            "cell_id": ["cell1"],
            "GENE_1": [1],
        }
    ).to_csv(reference_path / "reference_counts.csv", index=False)

    pd.DataFrame(
        {
            "cell_id": ["cell1"],
            "cell_type": ["A"],
        }
    ).to_csv(reference_path / "reference_labels.csv", index=False)
    (ground_truth_path / "params.json").write_text("{}")

    pd.DataFrame(
    {
        "square_id": ["s0", "s1", "s2", "s3"],
        "cell_type": ["A", "A", "A", "A"],
        "n_transcripts": [1, 2, 3, 4],
    }
    ).to_csv(
    ground_truth_path / "composition.csv",
    index=False,
    )

    pd.DataFrame(
    {
        "square_id": ["s0", "s1", "s2", "s3"],
        "domain": ["D1", "D1", "D1", "D1"],
    }
    ).to_csv(
    ground_truth_path / "domains.csv",
    index=False,
    )
    config_path = tmp_path / "config.yaml"
    config_path.write_text("bin_size_um: 4\n")

    binned = prepare_binned_counts(dataset_path, config_path)

    assert len(binned) == 1
    assert binned.loc[0, "bin_id"] == "bin_r0_c0"
    assert binned.loc[0, "GENE_1"] == 10
