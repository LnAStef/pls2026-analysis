"""Characterization tests for analysis output."""

import hashlib
from pathlib import Path

from spatial_decode.report import report_shape


def file_sha256(path):
    """Return the SHA-256 hash of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_reference_report_matches_golden_output(tmp_path):
    """Refactoring must preserve the reference dataset report."""
    report_shape(
        dataset_dir=Path("data/raw/reference_dataset"),
        results_dir=tmp_path,
        manifest_path=Path("data/raw_manifest.sha256"),
        config_path=Path("config/default.yaml"),
        seed=20260101,
    )

    actual_output = tmp_path / "dataset_shape.json"
    golden_output = Path("tests/golden/dataset_shape.json")

    assert file_sha256(actual_output) == file_sha256(golden_output)
