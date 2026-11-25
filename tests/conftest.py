"""Shared test fixtures.

Paths are resolved from the repository root, not from the directory pytest happens to be
started in, so `python -m pytest` behaves the same from anywhere inside the clone.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = REPO_ROOT / "data" / "raw"
REFERENCE_DATASET = RAW_DIR / "reference_dataset" / "dataset"
MANIFEST = REPO_ROOT / "data" / "raw_manifest.sha256"
DEFAULT_CONFIG = REPO_ROOT / "config" / "default.yaml"
GOLDEN_DIR = REPO_ROOT / "tests" / "golden"


@pytest.fixture
def reference_dataset():
    """Path to the course reference dataset, or skip if it has not been put in place.

    The dataset is not committed (see README, "Getting the data"). Tests that need it are
    skipped with a message saying where it should go, instead of failing with a checksum
    error that hides the real cause.
    """
    if not (REFERENCE_DATASET / "metadata.json").is_file():
        pytest.skip(
            f"reference dataset not found at {REFERENCE_DATASET.relative_to(REPO_ROOT)}/ "
            "- copy the course reference_dataset/ folder into data/raw/ (see README)"
        )
    return REFERENCE_DATASET
