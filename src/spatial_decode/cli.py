"""Command-line entry point: run the whole analysis and write every output to one folder.

Usage (from the repository root):

    python scripts/run_analysis.py \\
        --config config/default.yaml \\
        --data-dir data/raw/reference_dataset \\
        --out-dir results

Files written to --out-dir:

    predicted_composition.csv           bin_id, cell_type, fraction   (Data Contract §4)
    predicted_domains.csv               bin_id, domain   (smoothed)   (Data Contract §4)
    predicted_domains_unsmoothed.csv    bin_id, domain   (no smoothing, for comparison)
    scores.json                         RMSE, Jensen-Shannon divergence, ARI (Data Contract §5)
    run_metadata.json                   provenance: commit, config, seed, bin size, inputs

Inference (`run_analysis`) never reads ground_truth/; only the scoring step does.
"""

import argparse
import json
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import pandas as pd

from spatial_decode.config import load_config
from spatial_decode.pipeline import run_analysis
from spatial_decode.provenance import require_clean_manifest, stamp
from spatial_decode.scoring import score, score_domains

DEFAULT_MANIFEST = Path("data/raw_manifest.sha256")


def _tool_version():
    try:
        return version("spatial-decode")
    except PackageNotFoundError:
        return "unknown"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="run_analysis",
        description="Deconvolve a spatial dataset, detect domains, score against ground "
        "truth, and write all outputs to --out-dir.",
    )
    parser.add_argument(
        "--config", type=Path, default=Path("config/default.yaml"),
        help="analysis parameters (default: config/default.yaml)",
    )
    parser.add_argument(
        "--data-dir", type=Path, default=Path("data/raw/reference_dataset"),
        help="dataset folder holding metadata.json (default: data/raw/reference_dataset)",
    )
    parser.add_argument(
        "--out-dir", type=Path, default=Path("results"),
        help="where outputs are written; created if missing (default: results)",
    )
    parser.add_argument(
        "--manifest", type=Path, default=DEFAULT_MANIFEST,
        help="checksum manifest of the folder above --data-dir "
        "(default: data/raw_manifest.sha256)",
    )
    parser.add_argument(
        "--skip-manifest-check", action="store_true",
        help="do not verify input checksums (for datasets the manifest does not cover, "
        "e.g. one from a simulation-track group)",
    )
    return parser.parse_args(argv)


def _score_run(result, dataset_dir, bin_size_um, square_size_um):
    """Score predictions against ground truth. The only place ground_truth/ is read."""
    truth_dir = dataset_dir / "ground_truth"
    coordinates = pd.read_csv(dataset_dir / "coordinates.csv")
    truth_composition = pd.read_csv(truth_dir / "composition.csv")
    truth_domains = pd.read_csv(truth_dir / "domains.csv")

    scores = score(
        predicted_composition=result["predicted_composition"],
        predicted_domains=result["predicted_domains"],
        truth_composition=truth_composition,
        truth_domains=truth_domains,
        coordinates=coordinates,
        bin_size_um=bin_size_um,
        square_size_um=square_size_um,
    )
    # The aggregated truth matrix is a DataFrame, not a score; keep scores.json scalar-only.
    scores.pop("composition_matrix", None)

    scores["ari_unsmoothed"] = score_domains(
        predicted_domains=result["predicted_domains_unsmoothed"],
        truth_domains=truth_domains,
        coordinates=coordinates,
        bin_size_um=bin_size_um,
        square_size_um=square_size_um,
    )
    return scores


def main(argv=None):
    args = parse_args(argv)
    dataset_dir = args.data_dir.expanduser().resolve()
    out_dir = args.out_dir.expanduser()

    if not (dataset_dir / "metadata.json").is_file():
        sys.exit(
            f"error: no metadata.json in {dataset_dir}. Put the dataset there "
            "(see README, 'Getting the data') or pass --data-dir."
        )

    if not args.skip_manifest_check:
        require_clean_manifest(dataset_dir.parent, args.manifest)

    config = load_config(args.config)
    metadata = json.loads((dataset_dir / "metadata.json").read_text())

    result = run_analysis(dataset_dir, args.config)
    scores = _score_run(
        result, dataset_dir, config["bin_size_um"], metadata["square_size_um"]
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    result["predicted_composition"].to_csv(
        out_dir / "predicted_composition.csv", index=False
    )
    result["predicted_domains"].to_csv(out_dir / "predicted_domains.csv", index=False)
    result["predicted_domains_unsmoothed"].to_csv(
        out_dir / "predicted_domains_unsmoothed.csv", index=False
    )
    (out_dir / "scores.json").write_text(json.dumps(scores, indent=2) + "\n")

    run_metadata = stamp(
        config_path=args.config,
        seed=config["seed"],
        manifest_path=args.manifest if not args.skip_manifest_check else None,
    )
    run_metadata.update(
        {
            "tool": "spatial-decode",
            "tool_version": _tool_version(),
            "contract_version": metadata["contract_version"],
            "dataset": str(args.data_dir),
            "manifest_checked": not args.skip_manifest_check,
            "bin_size_um": config["bin_size_um"],
            "square_size_um": metadata["square_size_um"],
            "parameters": config,
            "command": sys.argv[:1] + (argv if argv is not None else sys.argv[1:]),
        }
    )
    (out_dir / "run_metadata.json").write_text(
        json.dumps(run_metadata, indent=2, default=str) + "\n"
    )

    print(f"Wrote outputs to {out_dir}/")
    for name, value in scores.items():
        print(f"  {name}: {value:.4f}")
    return 0
