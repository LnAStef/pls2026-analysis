# AI + verification log — Christian

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
