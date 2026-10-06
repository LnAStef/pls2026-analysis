from hashlib import sha256
from pathlib import Path


def manifest(root):
        """Fingerprint every file under a directory.

    Args:
        root: directory to scan, recursively.
    Returns:
        {relative_path: sha256 hex digest}, one entry per file, keyed by its path
        relative to `root`. Hashes are of the file's exact bytes (`read_bytes()`, not
        `read_text()`), since a text decode can silently change what gets hashed.
    """
    root = Path(root)

    result = {}

    for path in sorted(root.rglob("*")):
        if path.is_file():
            relative_path = path.relative_to(root).as_posix()
            digest = sha256(path.read_bytes()).hexdigest()
            result[relative_path] = digest

    return result



def write_manifest(m, path):
    """Write a manifest to disk, sorted, one file per line, in the format sha256sum uses.

    Args:
        m: {relative_path: sha256 hex digest}, as returned by `manifest()`.
        path: file to write, e.g. `data/raw_manifest.sha256`.
    """
    path = Path(path)

    path.write_text(
        "".join(
            f"{digest}  {name}\n"
            for name, digest in sorted(m.items())
        ),
        encoding="utf-8",
    )


def verify(root, manifest_path):
    """Compare a directory against a previously recorded manifest.

    Args:
        root: directory to check, e.g. `data/raw`.
        manifest_path: manifest file written by `write_manifest()` when `root` was last
            known good.
    Returns:
        {"changed": {...}, "missing": {...}, "added": {...}} — three sets of relative
        path strings. `changed` is in both but hashes differently; `missing` is in the
        manifest but not on disk; `added` is on disk but not in the manifest. An
        untouched directory returns three empty sets.
    """
    # YOUR TURN
    return {"changed": set(), "missing": set(), "added": set()}



    """Compare a directory against a previously recorded manifest."""
    root = Path(root)
    manifest_path = Path(manifest_path)

    # Manifest-Datei einlesen:
    # Format: sha256-hash zwei Leerzeichen relativer/pfad
    expected = {}

    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        digest, separator, name = line.partition("  ")

        if not separator:
            raise ValueError(f"Invalid manifest line: {line!r}")

        expected[name] = digest

    # Aktuellen Zustand des Ordners berechnen
    actual = manifest(root)

    expected_names = set(expected)
    actual_names = set(actual)

    changed = {
        name
        for name in expected_names & actual_names
        if expected[name] != actual[name]
    }

    missing = expected_names - actual_names
    added = actual_names - expected_names

    return {
        "changed": changed,
        "missing": missing,
        "added": added,
    }