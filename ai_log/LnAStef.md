## 2026-10-14 — deconvolve: NNLS-based cell-type composition per bin
 
- **Prompt / question:** "Assist me in writing deconvolve(S, binned_counts) that runs NNLS per
  bin and returns transcript fractions per cell type"
- **What it produced:** I built the function iteratively with AI guidance
- **How I checked it:**
  - known-answer test — 2 bins, 2 genes, 2 cell types; pure type-A bin returns
    `[1., 0.]`, pure type-B bin returns `[0., 1.]`
  - characterization test — hashed output on tiny fixed input, golden committed
- **What was wrong:** two bugs found during development:
  1. `nnls` returns a tuple `(w, residual)` — needed `w, _ = nnls(...)`
  2. `fractions = w.sum()` collapsed to a scalar — should be `w / w.sum()`
- **Decision:** accepted after known-answer test passed and golden hash committed

---

## 2026-10-14 — deconvolve.py: code review and cleanup
 
- **Prompt / question:** "review variable names and docstring in deconvolve()"
- **What it produced:** renamed variables for clarity, rewrote docstring with
  Args/Returns sections
- **How I checked it:** read-through — no functional change, only naming and
  documentation
- **What was wrong:**
  1. `S = S / S.sum()` overwrote the input argument — renamed to `S_normalised`
  2. `result_fractions_list` too verbose — renamed to `fractions_per_bin`
  3. `row` unclear — renamed to `bin_vector`
  4. `w` too cryptic — renamed to `weights`
  5. docstring lacked Args/Returns sections with types and shapes
- **Decision:** accepted — cleaner and more readable, output unchanged

---

## 2026-11-03 — deconvolve: labelled output, genes aligned by name, empty bins

- **Prompt / question:** "Repair the deconvolution interfaces: return a labelled
  composition instead of anonymous arrays, align genes by name instead of
  positional .values, and decide what an empty-transcript bin returns. Add two
  doctests."
- **What it produced:** deconvolve() now returns a DataFrame (bins x cell types)
  and raises ValueError on mismatched gene names; the maths is split into two
  small helpers, normalise_columns() and to_fractions(), each with a doctest
- **How I checked it:**
  - doctests for deconvolve.py pass
  - four new tests: labelled output, gene-order invariance (metamorphic), empty
    bin returns NaN, mismatched genes raise ValueError
  - known-answer test: A = 10 and B = 30 transcripts per cell, equal transcript
    amounts in the bin, gives 0.5 / 0.5, not 0.75 / 0.25
  - the golden hash did not change after hashing `result.to_numpy().tolist()`,
    so the numbers are identical and only the return type changed
- **What was wrong:**
  1. the old version returned anonymous arrays, so nothing said which column was
     which cell type
  2. genes were matched by position (`.values`), so a different gene order would
     silently give wrong results
  3. an empty bin divided by zero (`w / w.sum()`)
  4. the first suggested fix skipped empty bins with an extra `continue`; this was
     redundant, because all-zero counts already give all-zero weights and
     to_fractions() returns NaN, so I removed it
  5. the old characterization and known-answer tests failed after the change
     (iterating a DataFrame gives column names): expected, updated deliberately
- **Decision:** accepted; empty bins return NaN because their composition is
  undefined, and Data Contract §5 excludes them from scoring

---