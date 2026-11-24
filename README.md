# spatial-decode project

**Group:** Catalina, Vera, Christian, Janine and Elena  
**Track:** analysis (`spatial-decode`)

## What is this?

`spatial-decode` estimates, from synthetic spatial-transcriptomics data, which cell types each
spatial bin contains and which tissue domain each bin belongs to, then scores both against the
simulator's ground truth.

One command runs the whole pipeline:

1. checks the input files against the committed checksum manifest;
2. bins the 2 µm squares into larger bins (`bin_size_um` in the config);
3. estimates cell-type signatures from the single-cell reference;
4. estimates each bin's cell-type composition with non-negative least squares (NNLS);
5. detects spatial domains with KMeans, with and without spatial smoothing;
6. scores the predictions (RMSE, Jensen–Shannon divergence, ARI) and writes everything to `results/`.

Input and output formats follow the course Data Contract.

## Installation

From the repository root:

```bash
conda env create -f environment.yml
conda activate pls2026
pip install -e .
```

Nothing else needs installing by hand.

## Getting the data

The dataset is **not** in this repository. Use the course reference dataset (the
`reference_dataset/` folder shipped with the pre-course material) and copy it to:

```text
data/
├── raw_manifest.sha256          # committed: checksums of the files below
└── raw/
    └── reference_dataset/
        ├── metadata.json
        ├── coordinates.csv
        ├── counts.csv
        ├── reference/
        │   ├── reference_counts.csv
        │   └── reference_labels.csv
        └── ground_truth/        # read only by scoring and tests, never by inference
            ├── params.json
            ├── composition.csv
            └── domains.csv
```

```bash
mkdir -p data/raw
cp -r /path/to/reference_dataset data/raw/
chmod -R a-w data/raw          # optional: protect the inputs from accidental edits
```

`data/raw/` is ignored by git. The run refuses to start if any file there differs from
`data/raw_manifest.sha256`.

## Running the analysis

```bash
python scripts/run_analysis.py --config config/default.yaml --data-dir data/raw/reference_dataset --out-dir results
```

These are also the defaults, so `python scripts/run_analysis.py` does the same. After
`pip install -e .`, the same command is available as `spatial-decode`. `--help` lists every option.

Scientific parameters (bin size, number of domains, smoothing radius, seed) are in
`config/default.yaml`. The square size comes from the dataset's `metadata.json`.

**Datasets from a simulation-track group** are not covered by our manifest. Run them with
`--skip-manifest-check`; `run_metadata.json` then records `"manifest_checked": false`.

## Output files

Every run writes these files to `--out-dir` (default `results/`, ignored by git, safe to
delete):

| File | Contents |
|---|---|
| `predicted_composition.csv` | `bin_id, cell_type, fraction`: one row per bin and cell type. Fractions sum to 1 per bin; zero-transcript bins are NaN. |
| `predicted_domains.csv` | `bin_id, domain`: domain label per bin, after spatial smoothing. Bins with no transcripts get `-1`. |
| `predicted_domains_unsmoothed.csv` | Same format, without smoothing (for comparison). |
| `scores.json` | `rmse`, `jensen_shannon_divergence`, `ari` (smoothed), `ari_unsmoothed`. |
| `run_metadata.json` | Git commit, whether the tree was clean, config path and full parameters, seed, `bin_size_um`, contract and tool version, input-manifest checksum, command line and timestamp. |

Rerunning with the same config, seed and data reproduces every file byte for byte, except the
`created` timestamp in `run_metadata.json` (tested in `tests/test_cli.py`).

## Repository layout

```text
src/spatial_decode/   importable analysis code (cli.py is the entry point)
scripts/              run_analysis.py: the one-command run
tests/                automated tests; tests/golden/ holds characterization outputs
config/               analysis parameters (default.yaml)
data/                 raw_manifest.sha256 (committed); raw/ is where you put the dataset
ai_log/               individual AI-use and verification logs
SPEC.md               requirements and acceptance criteria
```

## Checks

From the repository root:

```bash
python -m pytest -q
python -m pytest --doctest-modules -q
ruff check .
```

Without the dataset in `data/raw/reference_dataset/`, the two reference-dataset tests
(`test_smoke.py`, `test_characterization.py`) are **skipped** and tell you where the data should
go. Everything else runs on small synthetic inputs built inside the tests.

---

The sections below are stubs. Each is filled in during the week named, and together they are what
makes this repository runnable by someone who has never met you. The long-form explanation of what a
runner does with them is the course document *Running a project from GitHub* — do not copy it in
here; a README is answers, not a manual.

## Run in a container *(Week 11)*

There are two separate things here. **A** happens on GitHub without anyone doing anything; **B** is
optional and is the only part that needs software on your computer. Fill in both.

### A. Built and run on GitHub — nothing to install

Every push, the `build-image` workflow builds this project's image from the `Dockerfile`, publishes
it, and runs the analysis inside it. This happens on GitHub's machines, so it works whether or not
anyone in this group — or anyone reading this — has Docker.

* **Image:** `<ghcr.io/your-group/your-project:tag>`
* **A recent successful build:** `<link to the workflow run>`

<**Where to find both.** On your repository page, the *Packages* panel on the right lists the image;
click it and the page shows the full name and every tag that has been published. The *Actions* tab
lists the workflow runs — open the most recent green `image` run and copy its URL.

The name is not a mystery once you have seen it: it is `ghcr.io/` + the owner and repository, in
lower case, exactly as they appear in your GitHub URL. So `github.com/Ada-Group/spatial-decode`
publishes to `ghcr.io/ada-group/spatial-decode`. The **tag** after the colon is added by the
workflow: `sha-3f9a1c2` for the commit it was built from, and the branch name for the latest build
on that branch. Use the commit tag here — it names one exact version, which `main` does not.>

<If the *Packages* panel is empty, the workflow has not published yet: check the *Actions* tab for a
failed run. If it is there but a classmate cannot pull it, the package is private — open it, then
*Package settings → Change visibility → Public*.>

### B. Running the image yourself — needs Docker or Podman

**Optional.** Only do this if you want the image on your own machine; the project is fully usable
without it, through the *Install* and *Run* sections above. Installing a runtime needs administrator
rights, and on macOS or Windows it runs a Linux virtual machine.

```bash
<docker pull ghcr.io/your-group/your-project:tag>
<docker run --rm \
    -v "$PWD/data:/data:ro" \
    -v "$PWD/results:/results" \
    ghcr.io/your-group/your-project:tag --data-dir /data/raw --out-dir /results>
```

<`podman` takes the same arguments. The two `-v` options are what give the container your data and
somewhere to write; without them it can see neither.>

## Run the whole pipeline *(Week 12)*

```bash
<nextflow run main.nf -profile conda ...>      # conda: no container runtime needed
<nextflow run main.nf -profile docker ...>     # docker: what CI uses, if the reader has it
```

## Verifying you got the right answer *(Week 13–14)*

<The result a correct run produces on the reference dataset — a number, or the checksums of the
output files. Say whether agreement should be exact or to a tolerance, and why.>

## Citation and version *(Week 14)*

<The version this README describes, and the DOI. `CITATION.cff` holds the full record.

In this course the deposit is made on sandbox.zenodo.org, so the DOI starts with 10.5072 and the
record is a practice one — say that here for complete clarity.>

## License *(Week 14)*

<The license your group chose, matching the LICENSE file.>
