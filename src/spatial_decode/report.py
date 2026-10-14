"""Week 3 report-analysis track."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from spatial_decode.provenance import require_clean_manifest, stamp


def report_shape(
    dataset_dir,
    results_dir,
    manifest_path=Path("data/raw_manifest.sha256"),
    config_path=Path("config/default.yaml"),
    seed=20260101,
):
    """Loads the reference dataset, reports its shape and writes provenance.

    Args:
        dataset_dir: Path to the reference dataset directory.
        results_dir: Directory where generated outputs should be written.
        manifest_path: Path to the committed raw-data checksum manifest.
        config_path: Configuration file associated with the run.
        seed: Random seed associated with the run.

    Returns:
        Dictionary containing the shapes of the loaded count tables.
    """
    dataset_dir = Path(dataset_dir)
    results_dir = Path(results_dir)
    manifest_path = Path(manifest_path)

    raw_root = dataset_dir.parent

    require_clean_manifest(
        raw_root,
        manifest_path,
    )

    counts = pd.read_csv(dataset_dir / "counts.csv")

    reference_counts = pd.read_csv(dataset_dir / "reference" / "reference_counts.csv")

    shape_report = {
        "spatial_counts_shape": list(counts.shape),
        "reference_counts_shape": list(reference_counts.shape),
    }

    print("Spatial counts shape:", counts.shape)
    print("Reference counts shape:", reference_counts.shape)

    results_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    (results_dir / "dataset_shape.json").write_text(
        json.dumps(
            shape_report,
            indent=2,
        )
    )

    (results_dir / "run_metadata.json").write_text(
        json.dumps(
            stamp(
                config_path=config_path,
                seed=seed,
                manifest_path=manifest_path,
            ),
            indent=2,
        )
    )

    return shape_report
