import json

import pandas as pd
import yaml

from spatial_decode.pipeline import run_analysis


def test_run_analysis_connects_all_analysis_steps(tmp_path):
    """Run the analysis pipeline on a small synthetic dataset."""
    dataset_path = tmp_path / "dataset"
    reference_path = dataset_path / "reference"
    ground_truth_path = dataset_path / "ground_truth"

    reference_path.mkdir(parents=True)
    ground_truth_path.mkdir()

    # Dataset metadata: each input square is 2 um.
    metadata = {
        "contract_version": "1.0",
        "square_size_um": 2,
        "grid": {
            "n_rows": 2,
            "n_cols": 2,
        },
        "cell_types": ["A", "B"],
    }
    (dataset_path / "metadata.json").write_text(json.dumps(metadata))

    # Four squares arranged as a 2 x 2 grid.
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
    coordinates.to_csv(dataset_path / "coordinates.csv", index=False)

    # Two genes with deliberately different mixtures across squares.
    counts = pd.DataFrame(
        {
            "square_id": [
                "sq_r0_c0",
                "sq_r0_c1",
                "sq_r1_c0",
                "sq_r1_c1",
            ],
            "Gene1": [10, 0, 8, 2],
            "Gene2": [0, 10, 2, 8],
        }
    )
    counts.to_csv(dataset_path / "counts.csv", index=False)

    # Reference cell A expresses Gene1, while B expresses Gene2.
    reference_counts = pd.DataFrame(
        {
            "cell_id": ["cell_A", "cell_B"],
            "Gene1": [10, 0],
            "Gene2": [0, 10],
        }
    )
    reference_counts.to_csv(
        reference_path / "reference_counts.csv",
        index=False,
    )

    reference_labels = pd.DataFrame(
        {
            "cell_id": ["cell_A", "cell_B"],
            "cell_type": ["A", "B"],
        }
    )
    reference_labels.to_csv(
        reference_path / "reference_labels.csv",
        index=False,
    )

    # Ground truth required by the Data Contract.
    (ground_truth_path / "params.json").write_text("{}")

    truth_composition = pd.DataFrame(
        {
            "square_id": [
                "sq_r0_c0",
                "sq_r0_c1",
                "sq_r1_c0",
                "sq_r1_c0",
                "sq_r1_c1",
                "sq_r1_c1",
            ],
            "cell_type": [
                "A",
                "B",
                "A",
                "B",
                "A",
                "B",
            ],
            "n_transcripts": [
                10,
                10,
                8,
                2,
                2,
                8,
            ],
        }
    )
    truth_composition.to_csv(
        ground_truth_path / "composition.csv",
        index=False,
    )

    truth_domains = pd.DataFrame(
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
    truth_domains.to_csv(
        ground_truth_path / "domains.csv",
        index=False,
    )

    # bin_size_um = square_size_um means each square becomes one analysis bin.
    config = {
        "seed": 20260101,
        "bin_size_um": 2,
        "n_domains": 2,
        "smoothing_radius": 0,
        "kmeans_n_init": 10,
    }

    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config))

    result = run_analysis(dataset_path, config_path)

    assert len(result["binned_counts"]) == 4

    assert result["signatures"].shape == (2, 2)
    assert list(result["signatures"].columns) == ["A", "B"]

    composition = result["predicted_composition"]

    assert set(composition.columns) == {
        "bin_id",
        "cell_type",
        "fraction",
    }

    # Four bins x two cell types.
    assert len(composition) == 8

    fraction_sums = composition.groupby("bin_id")["fraction"].sum()
    assert (fraction_sums.round(10) == 1.0).all()

    domains = result["predicted_domains"]
    assert set(domains.columns) == {"bin_id", "domain"}
    assert len(domains) == 4

    unsmoothed_domains = result["predicted_domains_unsmoothed"]
    assert set(unsmoothed_domains.columns) == {"bin_id", "domain"}
    assert len(unsmoothed_domains) == 4
