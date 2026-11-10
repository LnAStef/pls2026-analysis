import json

import pandas as pd
import pytest

from spatial_decode.validate import ContractViolation, validate_dataset


@pytest.fixture
def valid_dataset(tmp_path):
    """Create a minimal Data Contract-conforming dataset."""
    dataset = tmp_path / "dataset"
    reference = dataset / "reference"
    ground_truth = dataset / "ground_truth"

    reference.mkdir(parents=True)
    ground_truth.mkdir()

    metadata = {
        "contract_version": "1.0",
        "square_size_um": 2,
        "grid": {
            "n_rows": 2,
            "n_cols": 2,
        },
        "cell_types": ["A", "B"],
    }

    (dataset / "metadata.json").write_text(
        json.dumps(metadata)
    )

    coordinates = pd.DataFrame(
        {
            "square_id": [
                "sq_r0_c0",
                "sq_r0_c1",
                "sq_r1_c0",
                "sq_r1_c1",
            ],
            "array_row": [0, 0, 1, 1],
            "array_col": [0, 1, 0, 1],
            "x_um": [1.0, 3.0, 1.0, 3.0],
            "y_um": [1.0, 1.0, 3.0, 3.0],
        }
    )
    coordinates.to_csv(
        dataset / "coordinates.csv",
        index=False,
    )

    counts = pd.DataFrame(
        {
            "square_id": [
                "sq_r0_c0",
                "sq_r0_c1",
                "sq_r1_c0",
                "sq_r1_c1",
            ],
            "GENE_1": [5, 0, 2, 0],
            "GENE_2": [0, 4, 1, 0],
        }
    )
    counts.to_csv(
        dataset / "counts.csv",
        index=False,
    )

    reference_counts = pd.DataFrame(
        {
            "cell_id": ["cell_A", "cell_B"],
            "GENE_1": [10, 0],
            "GENE_2": [0, 10],
        }
    )
    reference_counts.to_csv(
        reference / "reference_counts.csv",
        index=False,
    )

    reference_labels = pd.DataFrame(
        {
            "cell_id": ["cell_A", "cell_B"],
            "cell_type": ["A", "B"],
        }
    )
    reference_labels.to_csv(
        reference / "reference_labels.csv",
        index=False,
    )

    # Ground truth composition is sparse:
    # missing square/cell-type combinations mean zero.
    composition = pd.DataFrame(
        {
            "square_id": [
                "sq_r0_c0",
                "sq_r0_c1",
                "sq_r1_c0",
                "sq_r1_c0",
            ],
            "cell_type": ["A", "B", "A", "B"],
            "n_transcripts": [5, 4, 2, 1],
        }
    )
    composition.to_csv(
        ground_truth / "composition.csv",
        index=False,
    )

    domains = pd.DataFrame(
        {
            "square_id": [
                "sq_r0_c0",
                "sq_r0_c1",
                "sq_r1_c0",
                "sq_r1_c1",
            ],
            "domain": ["D1", "D1", "D2", "D2"],
        }
    )
    domains.to_csv(
        ground_truth / "domains.csv",
        index=False,
    )

    (ground_truth / "params.json").write_text("{}")

    return dataset


def test_valid_dataset_is_accepted(valid_dataset):
    """A conforming dataset should pass validation silently."""
    assert validate_dataset(valid_dataset) is None


def test_missing_file_is_rejected(valid_dataset):
    """A missing required file should raise FileNotFoundError."""
    (valid_dataset / "counts.csv").unlink()

    with pytest.raises(
        FileNotFoundError,
        match="counts.csv",
    ):
        validate_dataset(valid_dataset)


def test_wrong_column_is_rejected(valid_dataset):
    """A required column with the wrong name should be rejected."""
    path = valid_dataset / "coordinates.csv"
    coordinates = pd.read_csv(path)

    coordinates = coordinates.rename(
        columns={"x_um": "x_position"}
    )
    coordinates.to_csv(path, index=False)

    with pytest.raises(
        ContractViolation,
        match="missing required column",
    ):
        validate_dataset(valid_dataset)


def test_negative_count_is_rejected(valid_dataset):
    """Transcript counts must be non-negative integers."""
    path = valid_dataset / "counts.csv"
    counts = pd.read_csv(path)

    counts.loc[0, "GENE_1"] = -1
    counts.to_csv(path, index=False)

    with pytest.raises(
        ContractViolation,
        match="non-negative integers",
    ):
        validate_dataset(valid_dataset)


def test_mismatched_square_ids_are_rejected(valid_dataset):
    """Counts and coordinates must contain matching square IDs."""
    path = valid_dataset / "counts.csv"
    counts = pd.read_csv(path)

    counts.loc[0, "square_id"] = "sq_unknown"
    counts.to_csv(path, index=False)

    with pytest.raises(
        ContractViolation,
        match="square_ids differ",
    ):
        validate_dataset(valid_dataset)


def test_composition_sum_mismatch_is_rejected(valid_dataset):
    """Ground-truth transcript totals must match counts.csv."""
    path = (
        valid_dataset
        / "ground_truth"
        / "composition.csv"
    )
    composition = pd.read_csv(path)

    # sq_r0_c0 has 5 transcripts in counts.csv,
    # so changing its truth total to 4 must fail.
    composition.loc[0, "n_transcripts"] = 4
    composition.to_csv(path, index=False)

    with pytest.raises(
        ContractViolation,
        match="per-type n_transcripts sum",
    ):
        validate_dataset(valid_dataset)
