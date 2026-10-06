# tests/test_provenance.py
from spatial_decode.provenance import manifest, write_manifest, verify


def a_small_raw_directory(tmp_path):
    """Build a throwaway raw directory with one file, and record its manifest."""
    root = tmp_path / "raw"
    root.mkdir()
    (root / "counts.csv").write_text("square_id,g1\nsq_r000_c000,7\n")
    manifest_path = tmp_path / "raw_manifest.sha256"
    write_manifest(manifest(root), manifest_path)
    return root, manifest_path

def test_silent_on_an_untouched_directory(tmp_path):
    root, manifest_path = a_small_raw_directory(tmp_path)
    assert verify(root, manifest_path) == {"changed": set(), "missing": set(), "added": set


def test_reports_a_modified_file_as_changed(tmp_path):
    root, manifest_path = a_small_raw_directory(tmp_path)
    (root / "counts.csv").write_text("square_id,g1\nsq_r000_c000,999\n")
    assert verify(root, manifest_path)["changed"] == {"counts.csv"}