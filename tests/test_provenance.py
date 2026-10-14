"""Tests for raw-data provenance checks."""

import pytest

from spatial_decode.provenance import (
    manifest,
    require_clean_manifest,
    verify,
    write_manifest,
)


def a_small_raw_directory(tmp_path):
    """Build a throwaway raw directory and record its manifest."""
    root = tmp_path / "raw"
    root.mkdir()

    (root / "counts.csv").write_text("square_id,g1\nsq_r000_c000,7\n")

    manifest_path = tmp_path / "raw_manifest.sha256"

    write_manifest(
        manifest(root),
        manifest_path,
    )

    return root, manifest_path


def test_silent_on_an_untouched_directory(tmp_path):
    root, manifest_path = a_small_raw_directory(tmp_path)

    assert verify(
        root,
        manifest_path,
    ) == {
        "changed": set(),
        "missing": set(),
        "added": set(),
    }


def test_reports_a_modified_file_as_changed(tmp_path):
    root, manifest_path = a_small_raw_directory(tmp_path)

    (root / "counts.csv").write_text("square_id,g1\nsq_r000_c000,999\n")

    assert verify(
        root,
        manifest_path,
    )["changed"] == {"counts.csv"}


def test_modified_raw_file_stops_the_program(tmp_path):
    root, manifest_path = a_small_raw_directory(tmp_path)

    (root / "counts.csv").write_text("square_id,g1\nsq_r000_c000,999\n")

    with pytest.raises(
        RuntimeError,
        match="Raw-data verification failed",
    ):
        require_clean_manifest(
            root,
            manifest_path,
        )
