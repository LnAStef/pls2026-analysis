"""Smoke test for week3."""

import json
from pathlib import Path

from spatial_decode.report import report_shape


def test_program_runs_end_to_end(tmp_path, capsys):
    """Load the reference dataset and produce Week 3 outputs."""
    report_shape(
        dataset_dir=Path("data/raw/reference_dataset"),
        results_dir=tmp_path,
        manifest_path=Path("data/raw_manifest.sha256"),
        config_path=Path("config/default.yaml"),
        seed=20260101,
    )

    shape_path = tmp_path / "dataset_shape.json"

    metadata_path = tmp_path / "run_metadata.json"

    assert shape_path.exists()
    assert metadata_path.exists()

    shape_report = json.loads(shape_path.read_text())

    assert shape_report["spatial_counts_shape"] == [25600, 101]

    assert shape_report["reference_counts_shape"] == [240, 101]

    printed = capsys.readouterr().out

    assert "Spatial counts shape:" in printed
    assert "Reference counts shape:" in printed
