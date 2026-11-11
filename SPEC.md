# spatial-decode (Analysis Track)

## Tool Description

Using synthetic spatial transcriptomics data (2 um square counts + coordinates + a single-cell reference) to recover  hidden tissue structure. 
This includes firstly binning the squares of the tissue. Then comes deconvolution, that is estimating the fraction transcripts that came from each cell type in each bin. 
In addition, the pipeline detects (partitioning) the spatial domains and evaluates the  performance against the simulator's ground truth.


## Inputs

**counts.csv** - Transcript counts at 2 um resolution (160x160 = 25,600 squares), binned by the pipeline to 8 um or 16 um. 
                 Integer dtype, no negative values. Bin size is a parameter, not hardcoded.

**reference/** - Single-cell reference experiment used to estimate per-type expression signatures. Has cell-type labels.

**coordinates.csv** - Spatial position (um) of every 2 um square. Used for binning and spatial smoothing.

**ground_truth/** - Answer key used only for scoring, never for inference. Stores transcript counts per cell type per square (not fractions), 
                    so that aggregation to any bin size is correct: sum counts over the block, then divide. ground_truth/params.json lists the 15 marker genes (5 per type).

**cell types**: Three cell types: A, B, C. RNA content ratio roughly 1 : 1.8 : 1.3 - fraction of transcripts and fraction of cells are not the same number.


## Outputs

**composition matrix** - Of shape (N_bins, N_types) - fractions >=0, summing to 1 across types for every non-empty bin. A bin with zero transcripts has an undefined composition and is returned as NaN (excluded from scoring, Data Contract section 5).

**ARI score** - Scalar, Comparing recovered domain assignments to ground-truth labels, computed per 2 um square (a bin's predicted label applies to every square in it).

Optionally: composition RMSE and Jensen-Shannon divergence against ground truth.


## Acceptance Criteria 

**[smoke test]** The pipeline runs end to end, including loading data, running deconvolution and writing scores, on the toy data set of 400 cells, without raising an exception.

**[metamorphic test]** ARI at 0.2x signal is lower than ARI at 1x signal.

**[reproducibility test]** Running the pipeline with the same seed, produces identical ARI scores every time.

**[schema / validation check]** The deconvolution output has shape (N_bins, N_types), all values are float and no entry is NaN, except in rows of zero-transcript bins.

**[schema / validation check]** Every (array_row, array_col) pair appears exactly once in coordinates.csv
                                and um coordinates agree with indices and square size, meaning the grid is complete.

**[property check]** There must be binning consistency, meaning the four 8 um bins that tile a 16 um bin sum to it exactly, gene by gene. 

**[reproducibility test]** A teammate who has never run this project can create the environment from environment.yml, install the package with pip install -e .
                           and get a clean pytest run without installing anything else by hand.

**[schema/validation check]** The program refuses to run if any file under data/raw/ does not match the recorded checksum.

**[reproducibility test]** Deleting results/ and rerunning with the same config and seed reproduces the outputs. 

**[characterization test]** deconvolve() output on a fixed tiny input (2 bins, 2 genes, 2 cell types) matches the committed golden hash — catches any accidental change after refactoring.

**[schema/validation test]** ruff check exits cleanly on the whole package. 

**[characterization test]** Running ruff format does not change the program's output: the result hash matches the value recorded in week 4. 

**[known-answer test]** pytest --doctest-modules passes: every example in every docstring produces what the docstring says it does.

**[schema/validation check]** Every file path mentioned in the README exists in the repository. 

**[known-answer test]** For a bin built from equal transcript amounts of two cell types whose cells differ 3-fold in RNA content, the estimated fractions are 0.5 / 0.5 (not 0.75 / 0.25).

**[property test]** For every non-empty bin, on any valid input dataset, the predicted fractions are all >= 0 and sum to 1 (within 1e-3). Zero-transcript bins are NaN.

**[metamorphic test]** On the reference dataset at 8 µm, spatial smoothing improves domain recovery: ARI(smoothed) > ARI(unsmoothed), and ARI(smoothed) > 0.7.


## First Known Answer - tiny input whose correct output we can state by hand

Type A expresses gene 1 and contains 10 transcripts per cell. Type B expresses gene 2 and contains 30 transcripts per cell.

Reference signatures (transcripts per cell):
S_raw = [[10,  0],
        [ 0, 30]]

Column-normalized signatures:
S = [[1, 0],
    [0, 1]]

Observed counts:
y = [30, 30]

Thus, expected RNA contribution fractions:
A = 50%
B = 50%

However, because type B contains three times more RNA per cell:
cells_A = 30 / 10 = 3
cells_B = 30 / 30 = 1

Expected cell-number fractions:
A = 75%
B = 25%

Column-normalized signatures estimate RNA contribution fractions. To estimate actual cell-number fractions, differences in RNA content per cell must be accounted for.

The conversion is:
[f_c = \frac{q_c/r_c}{\sum_j q_j/r_j}]
where (q_c) is the RNA fraction and (r_c) is the RNA content per cell.

Equal RNA contributions do not necessarily mean equal numbers of cells.


## Criterion-to-check table

Each criterion above, its check type, and the test that implements it.
TBD means no test exists yet; the owner fills it in.

| Criterion | Check type | Test |
|---|---|---|
| pipeline runs end to end | smoke | `test_smoke.py::test_program_runs_end_to_end` |
| ARI at 0.2x signal lower than at 1x | metamorphic | TBD |
| same seed, identical ARI scores | reproducibility | `test_spatialdomaindetection.py::test_clustering_is_deterministic` (clustering step only) |
| deconvolution output shape, float, NaN only in empty bins | schema / validation | `test_deconvolve.py::test_deconvolve_is_labelled` |
| coordinates grid complete | schema / validation | TBD |
| 8 um bins sum to the 16 um bin, gene by gene | property | `test_binning.py::test_four_8um_bins_sum_to_one_16um_bin` |
| teammate can rebuild the environment, clean pytest | reproducibility | TBD |
| program refuses to run on checksum mismatch | schema / validation | `test_provenance.py::test_modified_raw_file_stops_the_program` |
| delete results/, rerun, same outputs | reproducibility | TBD |
| deconvolve() output matches the golden hash | characterization | `test_deconvolve.py::test_deconvolve_characterization` |
| ruff check exits cleanly | schema / validation | TBD (by hand, no CI) |
| ruff format does not change the output | characterization | `test_characterization.py::test_reference_report_matches_golden_output` |
| pytest --doctest-modules passes | known-answer | doctests in `deconvolve.py`, `estimate_cell_type_signatures.py`, `spatialdomaindetection.py` |
| every README path exists | schema / validation | TBD |
| equal transcripts, 3-fold RNA content: 0.5 / 0.5 | known-answer | `test_deconvolve.py::test_deconvolve_units_are_transcripts_not_cells` |
| non-empty fractions >= 0 and sum to 1 | property | `test_deconvolve.py::test_deconvolve_fractions_are_valid` |
| smoothing improves ARI at 8 um | metamorphic | `test_spatialdomaindetection.py::test_smoothing_improves_ari_on_noisy_data` |