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
