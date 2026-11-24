"""Tests for the one-command analysis entry point (scripts/run_analysis.py)."""

import json
import shutil

import pandas as pd
import pytest
import yaml

from spatial_decode.cli import main
from spatial_decode.provenance import manifest, write_manifest

OUTPUT_FILES = [
    "predicted_composition.csv",
    "predicted_domains.csv",
    "predicted_domains_unsmoothed.csv",
    "scores.json",
    "run_metadata.json",
]


@pytest.fixture
def tiny_run(tmp_path):
    """A 2 x 2 contract-conforming dataset under raw/, its manifest, and a config."""
    raw = tmp_path / "raw"
    dataset = raw / "tiny_dataset"
    (dataset / "reference").mkdir(parents=True)
    (dataset / "ground_truth").mkdir()

    squares = ["sq_r0_c0", "sq_r0_c1", "sq_r1_c0", "sq_r1_c1"]
    (dataset / "metadata.json").write_text(
        json.dumps(
            {
                "contract_version": "1.0",
                "square_size_um": 2,
                "grid": {"n_rows": 2, "n_cols": 2},
                "cell_types": ["A", "B"],
            }
        )
    )
    pd.DataFrame(
        {
            "square_id": squares,
            "array_row": [0, 0, 1, 1],
            "array_col": [0, 1, 0, 1],
            "x_um": [1.0, 3.0, 1.0, 3.0],
            "y_um": [1.0, 1.0, 3.0, 3.0],
        }
    ).to_csv(dataset / "coordinates.csv", index=False)
    pd.DataFrame(
        {"square_id": squares, "Gene1": [10, 0, 8, 2], "Gene2": [0, 10, 2, 8]}
    ).to_csv(dataset / "counts.csv", index=False)
    pd.DataFrame(
        {"cell_id": ["cell_A", "cell_B"], "Gene1": [10, 0], "Gene2": [0, 10]}
    ).to_csv(dataset / "reference" / "reference_counts.csv", index=False)
    pd.DataFrame({"cell_id": ["cell_A", "cell_B"], "cell_type": ["A", "B"]}).to_csv(
        dataset / "reference" / "reference_labels.csv", index=False
    )
    (dataset / "ground_truth" / "params.json").write_text("{}")
    pd.DataFrame(
        {
            "square_id": [squares[0], squares[1], squares[2], squares[2], squares[3], squares[3]],
            "cell_type": ["A", "B", "A", "B", "A", "B"],
            "n_transcripts": [10, 10, 8, 2, 2, 8],
        }
    ).to_csv(dataset / "ground_truth" / "composition.csv", index=False)
    pd.DataFrame({"square_id": squares, "domain": ["D1", "D2", "D1", "D2"]}).to_csv(
        dataset / "ground_truth" / "domains.csv", index=False
    )

    manifest_path = tmp_path / "raw_manifest.sha256"
    write_manifest(manifest(raw), manifest_path)

    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "seed": 20260101,
                "bin_size_um": 2,
                "n_domains": 2,
                "smoothing_radius": 0,
                "kmeans_n_init": 10,
            }
        )
    )
    return {"dataset": dataset, "manifest": manifest_path, "config": config_path}


def _run(tiny_run, out_dir):
    return main(
        [
            "--config", str(tiny_run["config"]),
            "--data-dir", str(tiny_run["dataset"]),
            "--out-dir", str(out_dir),
            "--manifest", str(tiny_run["manifest"]),
        ]
    )


def test_run_writes_every_documented_output(tiny_run, tmp_path):
    out_dir = tmp_path / "results"

    assert _run(tiny_run, out_dir) == 0

    for name in OUTPUT_FILES:
        assert (out_dir / name).is_file(), name

    composition = pd.read_csv(out_dir / "predicted_composition.csv")
    assert list(composition.columns) == ["bin_id", "cell_type", "fraction"]

    domains = pd.read_csv(out_dir / "predicted_domains.csv")
    assert list(domains.columns) == ["bin_id", "domain"]

    scores = json.loads((out_dir / "scores.json").read_text())
    assert set(scores) == {"rmse", "jensen_shannon_divergence", "ari", "ari_unsmoothed"}

    metadata = json.loads((out_dir / "run_metadata.json").read_text())
    assert metadata["bin_size_um"] == 2
    assert metadata["seed"] == 20260101
    assert metadata["contract_version"] == "1.0"
    assert metadata["manifest_checked"] is True


def test_deleting_results_and_rerunning_reproduces_outputs(tiny_run, tmp_path):
    """Same config and seed: every output except the run timestamp is byte-identical."""
    out_dir = tmp_path / "results"

    _run(tiny_run, out_dir)
    first = {name: (out_dir / name).read_bytes() for name in OUTPUT_FILES[:-1]}

    shutil.rmtree(out_dir)
    _run(tiny_run, out_dir)
    second = {name: (out_dir / name).read_bytes() for name in OUTPUT_FILES[:-1]}

    assert first == second


def test_refuses_to_run_when_raw_data_changed(tiny_run, tmp_path):
    counts = tiny_run["dataset"] / "counts.csv"
    counts.write_text(counts.read_text().replace("10", "11", 1))

    with pytest.raises(RuntimeError, match="Raw-data verification failed"):
        _run(tiny_run, tmp_path / "results")

    assert not (tmp_path / "results").exists()


def test_missing_dataset_gives_a_clear_message(tmp_path):
    with pytest.raises(SystemExit, match="no metadata.json"):
        main(["--data-dir", str(tmp_path / "nowhere"), "--out-dir", str(tmp_path / "r")])
