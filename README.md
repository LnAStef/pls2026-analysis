# spatial-decode project

**Group:** Catalina, Vera, Christian, Janine and Elena  
**Track:** analysis (`spatial-decode`)

## What is this?

`spatial-decode` is an analysis pipeline for synthetic spatial-transcriptomics data.

The project currently implements the main scientific components required by the analysis track:

- loading spatial transcript counts, coordinates, metadata, and the single-cell reference;
- aggregating square-level transcript counts into configurable spatial bins;
- estimating cell-type expression signatures from the single-cell reference;
- estimating cell-type composition in each spatial bin using non-negative least squares (NNLS);
- detecting spatial domains using smoothing and KMeans clustering;
- providing scoring utilities for comparison with simulated ground truth;
- recording provenance and checking raw-data integrity with manifests.

The spatial bin size is configurable. The original square size is read from the dataset metadata rather than hard-coded in the analysis.

The individual scientific components are implemented, but they are not yet connected through a single command-line entry point for the complete analysis workflow.

Input and output formats are defined by the course Data Contract and are not duplicated here.

## What do I need?

Create the project environment from the repository root:

```bash
conda env create -f environment.yml
conda activate pls2026
pip install -e .
```

The project requires a dataset that follows the course Data Contract.

The course reference dataset is not committed to this repository and should be supplied to the analysis by path. Its source and retrieval instructions will be documented here once the course-provided location is confirmed.

Analysis parameters are stored in:

```text
config/default.yaml
```

For example, the spatial bin size is read from this configuration file, while the original square size is read from the dataset `metadata.json`.

## How do I run it?

At the current stage of the project, the config-driven loading and spatial-binning stage can be run directly from Python.

Replace `<dataset-path>` with the directory containing the course reference dataset:

```bash
python -c "from spatial_decode.pipeline import prepare_binned_counts; b = prepare_binned_counts('<dataset-path>', 'config/default.yaml'); print(b.shape); print(b.head())"
```

This calls:

```python
prepare_binned_counts(dataset_path, config_path)
```

which:

1. loads the analysis configuration;
2. loads the dataset;
3. reads `bin_size_um` from `config/default.yaml`;
4. reads `square_size_um` from the dataset metadata;
5. aggregates square-level transcript counts into spatial bins.

The remaining analysis components — signature estimation, NNLS deconvolution, spatial-domain detection, and scoring — are implemented as separate modules and are being connected into the complete pipeline in later project work.

## What comes out?

`prepare_binned_counts()` returns a pandas DataFrame with one row per spatial bin.

It contains:

- `bin_id` — the spatial-bin identifier;
- `bin_row` and `bin_col` — the bin position on the spatial grid;
- one column per gene containing the summed transcript counts in that bin.

The raw input files are not modified.

Downstream analysis modules use the binned transcript counts to estimate cell-type composition and identify spatial domains.

## Repository layout

```text
src/        importable analysis code
tests/      automated tests and characterization checks
config/     analysis parameters
ai_log/     individual AI-use and verification logs
SPEC.md     project requirements and acceptance criteria
```

Raw datasets are not committed to the repository.

## Checks

Run the project checks from the repository root:

```bash
python -m pytest -q
python -m pytest --doctest-modules -q
ruff check .
```

`pytest --doctest-modules` runs the ordinary test suite together with executable examples contained in docstrings.

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
