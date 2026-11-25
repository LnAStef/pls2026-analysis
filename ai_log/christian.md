# AI + verification log — Christian

## 2026-11-25 — make the repo accept the reference dataset as shipped

- **Prompt / ask:** The Pre-course `reference_dataset/` has the data one level down in
  `dataset/` (plus `README.md`, `expected_scores.json` and macOS `._*` files), but the repo
  expected it flat in `data/raw/reference_dataset/`. Asked Claude to fix the mismatch, then
  clarified: change the repo to match the dataset, not the other way round, and update the README.
- **What it produced:**
  - default `--data-dir` → `data/raw/reference_dataset/dataset` (`cli.py`,
    `scripts/run_analysis.py`, `tests/conftest.py`)
  - `provenance.manifest()` skips `._*` and `.DS_Store`, plus a new test
    `test_macos_metadata_files_are_ignored`
  - `data/raw_manifest.sha256` regenerated with our own `manifest()`/`write_manifest()` for the
    shipped layout (now also covers the course `README.md` and `expected_scores.json`)
  - README "Getting the data" rewritten to show the folder exactly as shipped
- **How you checked it:**
  - copied the unchanged Pre-course folder (`._` files included) into `data/raw/` →
    `verify()` reports no changed/missing/added files
  - compared the new manifest with the old one: the 8 data-file hashes are identical, only the
    paths gained `dataset/`, so the data itself is the same as before
  - rebased onto the updated `main` (after #68 global RMSE and #69 spec/tests) → applied cleanly
  - `python -m pytest -q` → **74 passed, 0 skipped**. The two reference-dataset tests that were
    skipped on 2026-11-24 now run on the real data and pass, including the characterization test.
  - `ruff check .` → clean
  - `python scripts/run_analysis.py` with all defaults on the real data (8 µm bins): RMSE 0.0220,
    JSD 0.0061, ARI unsmoothed 0.482, ARI smoothed 0.909. Course `expected_scores.json` at 8 µm:
    RMSE 0.0220, JSD 0.0061, ARI 0.482 / 0.806. RMSE, JSD and unsmoothed ARI match the reference
    implementation; smoothed ARI is higher. (Before the global-RMSE change in #68 our RMSE was
    0.0152, so the expected-score match also confirms that change.)
    This closes the "still to do" from 2026-11-24 (ARI smoothed > 0.7 on the real dataset).
- **What was wrong:**
  1. Claude first misread the ask and did the opposite: it flattened the dataset into a zip to fit
     the old repo layout. That zip is obsolete and should not be used.
  2. Without the ignore rule, the `._*` files from unpacking on a Mac would count as "added"
     files, and the run would refuse to start even on correct data.
  3. Claude's first attempt to run the tests (`pip install -e .` + pytest) was blocked in its
     session; the tests were then run with `PYTHONPATH=src` instead.
  4. Pushing from the Claude session failed again (no write access). The change was exported as
     a patch to apply with `git am`.
  5. My first `git am` failed with "does not match index": I had uncommitted local edits in
     `cli.py`, `provenance.py` and `test_provenance.py`. Git refuses to patch over them.
     Fixed with `git am --abort`, then stashing/discarding the edits.
- **Decision:** accepted after the checks above. To do: rerun the tests on my machine before
  opening the PR.

---

## 2026-11-24 — make the analysis runnable and reproducible from a fresh clone

- **Prompt / ask:** Gave Claude the reviewer's feedback (priority list: fix repository-relative
  paths in the failing tests, rewrite README setup and data layout, add
  `scripts/run_analysis.py`, write outputs to `results/`, document the generated files, verify
  from a clean clone) and asked how to fix it, building on Vera's scoring update on
  `scoring_fix`.
- **What it produced:**
  - `tests/conftest.py`: dataset paths resolved from the repo root; reference-dataset tests skip
    with a message saying where the data goes
  - `src/spatial_decode/cli.py` + `scripts/run_analysis.py` (also the `spatial-decode` command):
    manifest check → full pipeline → scoring → `predicted_composition.csv`,
    `predicted_domains.csv`, `predicted_domains_unsmoothed.csv`, `scores.json`,
    `run_metadata.json` in `--out-dir`
  - `tests/test_cli.py` (4 tests), README rewritten, one row of the SPEC criterion table filled
- **How you checked it:**
  - from a clean copy (ignored files removed): `python -m pytest -q` → 46 passed, 2 skipped;
    `python -m pytest --doctest-modules -q` → 52 passed, 2 skipped; `ruff check .` → clean
  - ran from a different working directory (`tests/`) → same result, so the paths really are
    repo-relative
  - ran `scripts/run_analysis.py` on a generated 160×160, 100-gene stand-in dataset: all five
    files written, ~2 s
  - deleted `results/`, reran, compared `sha256sum` of the CSVs and `scores.json` → identical
  - put the stand-in into `data/raw/reference_dataset/` and ran without
    `--skip-manifest-check` → refused with "Raw-data verification failed", as it should
  - `test_cli.py` checks the same things automatically: outputs exist, delete-and-rerun is
    byte-identical, changed raw data is refused, a missing dataset gives a clear message
- **What was wrong:**
  1. The first draft of `cli.py` passed `manifest_path=None` to `provenance.stamp()`, which
     always hashes the manifest file. That would have crashed with `--skip-manifest-check`, so
     `stamp()` was changed to accept `None`.
  2. The first real run printed four pandas `PerformanceWarning`s from `binning.py`.
     A `.copy()` after the merge fixed this; output checksums unchanged.
  3. The first clean-copy check used `git clean -x`, which also deleted the new, not-yet-committed
     files and gave a false failure. Redone with `git clean -X` (ignored files only).
  4. Pushing from the Claude session failed: Claude has no write access to the repo. It was
     exported as a patch instead.
  5. Limitation: the stand-in dataset is synthetic, so its scores (ARI 0.98) say nothing about
     our real performance. **Still to do:** run on the real `reference_dataset/` and confirm the
     two skipped tests pass and ARI(smoothed) > 0.7.
- **Decision:** accepted after the checks above, pending the run on the real reference dataset.

---

## 2026-11-24 — review of Vera's "add composition matrix to scoring" (`scoring_fix`)

- **Prompt / ask:** "Should I approve 'add composition matrix to scoring'?"
- **What it produced:** a review recommending "request changes" and a comment to paste.
- **How you checked it:** read the diff (`git show 22ed4d4`), ran the test suite and ruff on
  the branch (both passed), and compared the behaviour against SPEC.md and the Data Contract §5.
  Added `test_empty_bin_is_nan_and_excluded_from_scoring` to pin the new behaviour: an empty
  bin stays in the matrix as NaN and does not change RMSE/JSD.
- **What was wrong (in the PR):**
  1. three debug `print()`s that dump full tables on the real dataset
  2. no test for the new NaN behaviour
  3. `composition_matrix` is the *ground-truth* matrix, not the predicted one; it was also
     computed twice, and a DataFrame inside the scores dict broke writing `scores.json`
  4. the multi-line calls were reformatted into very long lines, making the diff hard to review
- **Decision:** logic accepted (matches the SPEC). Prints removed and test added in
  `fix/reproducible-run`; requested changes on the PR. I did not edit Vera's AI log; that is
  hers to update.
