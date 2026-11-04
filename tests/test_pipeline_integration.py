import json

import pandas as pd
import yaml

from spatial_decode.pipeline import run_analysis


def test_run_analysis_connects_all_analysis_steps(tmp_path):
    """Run the analysis pipeline on a small synthetic dataset."""
    dataset_path = tmp_path / "dataset"
    reference_path = dataset_path / "reference"
    reference_path.mkdir(parents=True)

    # Dataset metadata: each input square is 2 um.
    metadata = {
        "square_size_um": 2,
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
            "x_um": [0.0, 2.0, 0.0, 2.0],
            "y_um": [0.0, 0.0, 2.0, 2.0],
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
