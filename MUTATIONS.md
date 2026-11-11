# Mutation record: deconvolve.py

Method: `run_mutations_deconvolve.py` copies the package to a temporary folder, applies one
mutation at a time to the copy, and runs `tests/test_deconvolve.py` on it, so the
real files are never modified. Run it with `python run_mutations_deconvolve.py` from the
project root. Predictions were not written down in advance for runs 1 and 2.

## Run 1: 7 tests

| # | Mutation | Result | Tests that failed |
|---|---|---|---|
| 1 | normalise_columns returns S unchanged | CAUGHT | characterization, units |
| 2 | genes matched by position, not name | CAUGHT | gene-order |
| 3 | no ValueError on mismatched genes | CAUGHT | mismatched genes |
| 4 | to_fractions returns raw weights | CAUGHT | characterization, known-answer, units |
| 5 | to_fractions without the zero-total guard | **SURVIVED** | none (1 RuntimeWarning) |
| 6 | rows normalised instead of columns | **SURVIVED** | none |

### Surviving mutants
- **5:** 0/0 still gives NaN, with only a RuntimeWarning, so the output is identical
  and no test noticed. Fixed by `test_deconvolve_empty_bin_is_nan_without_warning`,
  which turns warnings into errors.
- **6:** every S in my tests was symmetric or diagonal, so rows and columns normalise
  the same way. Fixed by `test_deconvolve_normalises_columns_not_rows`, which uses an
  asymmetric S with a hand-computed answer.

## Run 2: 12 tests, after adding the tests above

| # | Mutation | Result | Tests that failed |
|---|---|---|---|
| 1 | normalise_columns returns S unchanged | CAUGHT | characterization, columns-not-rows, units |
| 2 | genes matched by position, not name | CAUGHT | gene-order |
| 3 | no ValueError on mismatched genes | CAUGHT | mismatched genes |
| 4 | to_fractions returns raw weights | CAUGHT | 8 test runs, including the 3 parametrized cases |
| 5 | to_fractions without the zero-total guard | CAUGHT | empty-bin-without-warning |
| 6 | rows normalised instead of columns | CAUGHT | columns-not-rows |

No survivors. Mutants 5 and 6 were each caught by exactly one test, the ones added
after Run 1.

## Limits
- Six mutations of one function say that these six faults are noticed, and nothing
  about faults I did not try.
- deconvolve() is tested in isolation. pipeline.py does not call it yet, so a broken
  deconvolve() would not fail any pipeline test.
