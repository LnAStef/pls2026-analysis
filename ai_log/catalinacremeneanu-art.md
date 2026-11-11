
## Week 3 — Project structure, provenance and smoke testing

**What I asked:**  
I asked for help implementing a fail-closed manifest check, provenance output and an end-to-end smoke test.

**What it suggested:**  
I added an enforcing wrapper around the checksum comparison so that changed, missing, or added raw files stop the program. I also added a report function that verifies the raw manifest, loads the spatial and reference count tables, prints their shapes, writes `dataset_shape.json` and writes `run_metadata.json`.

**How I verified it:**  
The provenance tests deliberately modify a temporary raw-data file and confirm that the modified file is detected and that the enforcing check raises an exception. The smoke test runs the report end to end and checks that the expected output files are created. I also verified the known shapes of the reference data: spatial counts `(25600, 101)` and reference counts `(240, 101)`, and ran Ruff plus the full pytest suite.

**What I learned:**  
A passing check on untouched data is not enough to prove that protection works. The useful test deliberately introduces the failure condition and confirms that the program stops for the expected reason. I also learned why generated outputs belong outside Git while the checksum manifest belongs inside Git: the output is disposable, while the manifest records which raw bytes the analysis trusted.


### Week 4: implementing and testing the binning function

**What I asked:**  
I asked an AI assistant to help me implement a pure spatial binning function and to design tests for it.

**What it suggested:**  
The AI proposed a `bin_counts()` function that:
- takes spatial counts, coordinates, `bin_size_um`, and `square_size_um` as explicit inputs;
- calculates the number of squares per bin using `k = bin_size_um / square_size_um`;
- assigns squares to bins using integer division of `array_row` and `array_col`;
- sums gene counts within each bin;
- returns the binned counts without reading from or writing to files.

It also suggested two tests:
- a small known-answer test where four 2 um squares are summed into one 4 um bin;
- an aggregation test showing that four 8 um bins sum exactly to the corresponding 16 um bin, gene by gene.

**How I verified it:**  
I checked the implementation against the specification and Data Contract, which require exact summation of counts and configurable bin sizes. I then ran the tests with pytest. Both binning tests passed.


Week 5: code quality and deconvolution cleanup
What I asked:
I asked for help checking the analysis code against the course requirements, especially Ruff, test collection and the deconvolution workflow.
What it suggested:
The AI helped identify an indentation problem in the cell-signature test and highlighted that deconvolution should align genes by name rather than rely only on column order.
How I verified it:
I corrected the test, checked the deconvolution output and ran the affected tests together with Ruff.
What I learned:
I learned that labelled data structures are safer than relying on column order, because silent reordering can otherwise lead to incorrect results.

Week 6: connecting the analysis pipeline
What I asked:
I asked for help connecting the separate analysis functions into one workflow.
What it suggested:
The AI suggested a run_analysis() function that loads the dataset, performs binning, estimates cell-type signatures, runs NNLS deconvolution and detects spatial domains. It also suggested an integration test for the complete workflow.
How I verified it:
I ran the new integration test and checked the output structure, fraction sums and domain outputs. The test and Ruff both passed.
What I learned:
I learned the difference between having correct individual functions and having a complete pipeline. Integration tests are useful for checking whether the interfaces between the individual steps work correctly.

Week 7: dataset validation
What I asked:
I asked for help checking validate_dataset() against the Data Contract and adding the required validation tests.
What it suggested:
The AI helped identify missing required-file checks and suggested six tests: one valid dataset and five deliberately broken datasets covering a missing file, wrong column, negative count, mismatched square IDs and inconsistent composition totals. Validation was also added at the start of load_dataset().
How I verified it:
All six validation tests passed. After adding validation to the loader, some older test datasets failed because they were incomplete, so I updated them to conform to the Data Contract instead of weakening the validator.
What I learned:
I learned why validation should happen before the analysis starts and why a failing old test can sometimes reveal that the test fixture itself is invalid rather than that the new code is wrong.

Week 8: scoring and test-suite integration
What I asked:
I asked for help implementing the required scoring metrics.
What it suggested:
The AI suggested replacing the exploratory scoring.py with functions for RMSE, Jensen–Shannon divergence and ARI. It also suggested a known-answer test using a perfect prediction.
How I verified it:
I ran the scoring test, the full pytest suite, doctests and Ruff. I also checked that the ground-truth composition is summed into bins before converting to fractions.
What I learned:
I learned that scoring requires prediction and truth to be compared at the same spatial scale, and that transcript counts must be summed before calculating fractions. I also learned that SciPy returns Jensen–Shannon distance, so it must be squared to obtain the divergence required by the specification.

