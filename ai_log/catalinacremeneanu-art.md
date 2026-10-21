
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

