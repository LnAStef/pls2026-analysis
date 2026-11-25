import hashlib
from pathlib import Path

# macOS writes these when a folder is copied or unpacked (AppleDouble "._*" files,
# Finder's ".DS_Store"). They hold file-system metadata, not data, and appear or vanish
# depending on how the archive was extracted, so they are left out of the manifest.
_IGNORED_NAMES = {".DS_Store"}
_IGNORED_PREFIX = "._"


def _is_ignored(path):
    return path.name in _IGNORED_NAMES or path.name.startswith(_IGNORED_PREFIX)


def manifest(root):
    """Fingerprint every file under a directory.

    Args:
        root: directory to scan, recursively.
    Returns:
        {relative_path: sha256 hex digest}, one entry per file, keyed by its path
        relative to `root`. Hashes are of the file's exact bytes (`read_bytes()`, not
        `read_text()`), since a text decode can silently change what gets hashed.
        macOS metadata files (`._*`, `.DS_Store`) are skipped.
    """
    root = Path(root)
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file() and not _is_ignored(path)
    }


def write_manifest(m, path):
    """Write a manifest to disk, sorted, one file per line, in the format sha256sum uses.

    Args:
        m: {relative_path: sha256 hex digest}, as returned by `manifest()`.
        path: file to write, e.g. `data/raw_manifest.sha256`.
    """
    path = Path(path)
    path.write_text("".join(f"{h}  {name}\n" for name, h in sorted(m.items())))


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
    root = Path(root)
    manifest_path = Path(manifest_path)

    recorded = {}

    for line in manifest_path.read_text().splitlines():
        if not line:
            continue

        digest, name = line.split("  ", 1)
        recorded[name] = digest

    current = manifest(root)

    recorded_paths = set(recorded)
    current_paths = set(current)

    changed = {
        name
        for name in recorded_paths & current_paths
        if recorded[name] != current[name]
    }

    return {
        "changed": changed,
        "missing": recorded_paths - current_paths,
        "added": current_paths - recorded_paths,
    }


def require_clean_manifest(root, manifest_path):
    """Raise if raw data differ from the recorded manifest.

    Args:
        root: Directory whose files should match the manifest.
        manifest_path: Previously recorded checksum manifest.

    Returns:
        The clean verification report.

    Raises:
        RuntimeError: If a file was changed, removed, or added.
    """
    report = verify(root, manifest_path)

    if any(report.values()):
        raise RuntimeError(
            "Raw-data verification failed: "
            f"changed={sorted(report['changed'])}, "
            f"missing={sorted(report['missing'])}, "
            f"added={sorted(report['added'])}"
        )

    return report


def stamp(config_path, seed, manifest_path):
    """Build provenance metadata describing the current program run."""
    from datetime import datetime, timezone
    import platform
    import subprocess

    repo_root = Path(__file__).resolve().parents[2]
    source_path = Path(__file__).resolve()
    source_relative = source_path.relative_to(repo_root)

    try:
        subprocess.run(
            [
                "git",
                "ls-files",
                "--error-unmatch",
                str(source_relative),
            ],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )

        git_commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        git_status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout

        git_clean = git_status.strip() == ""

    except (subprocess.CalledProcessError, FileNotFoundError):
        git_commit = ""
        git_clean = False

    if manifest_path is None:
        manifest_digest = None  # run without a checksum manifest
    else:
        manifest_digest = hashlib.sha256(Path(manifest_path).read_bytes()).hexdigest()

    return {
        "git_commit": git_commit,
        "git_clean": git_clean,
        "config": str(config_path),
        "seed": seed,
        "input_manifest_sha256": manifest_digest,
        "created": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
    }
