# spatial-decode (Analysis Track)

## Tool Description

Using syntetic spatial transcriptomics data (2 um square counts + coordinates + a single-cell reference), the task is to try to recover the hidden structure. This includes firstly binning the squares of the tissue. Then comes deconvolution, that is estimating the fraction transcripts that came from each cell type in each bin. In addition, includes detecting(partitioning) the spatial domains and evaluating the model performance against the simulator's truth.


## Inputs

**counts.csv** - transcript counts at 2 um resolution (160x160 = 25,600 squares), binned by the pipeline to 8 um or 16 um. Shape (N_bins, G), integer dtype, no negative values. Bin size is a parameter, not hardcoded.

**reference/** - single-cell reference experiment used to estimate per-type expression signatures. Shape (N_cells, G) with cell-type labels.

**coordinates.csv** - spatial position (um) of every 2 um square, used for binning and spatial smoothing.

**ground_truth/** - answer key used only for scoring, never for inference. Stores transcript counts per cell type per square (not fractions), so that aggregation to any bin size is correct: sum counts over the block, then divide. ground_truth/params.json lists the 15 marker genes (5 per type).

Three **cell types**: A, B, C. RNA content ratio roughly 1 : 1.8 : 1.3 - fraction of transcripts and fraction of cells are not the same number.


## Outputs

A **composition matrix** of shape (N_bins, N_types) - fractions >=0, summing to 1 across types for every bin.

A scalar **ARI score** comparing recovered domain assignments to ground-truth labels, computed per 2 um square (a bin's predicted label applies to every square in it).

Optionally: composition RMSE and Jensen-Shannon divergence against ground truth.


## Acceptance Criteria 

**[smoke test]** The pipeline runs end to end, including loading data, running deconvolution and writing scores, on the toy datasetof 400 cells, without raising an exception.

**[property check]** The output fractions of deconvolution per bin are >=0 and sum to 1 for every spatial bin.

**[metamorphic test]** ARI at 0.2xsignal is lower than ARI at 1x signal.

**[reproducibility test]** Running the pipeline with the same seed, produces identical ARI scores every time.

**[schema / validation check]** The deconvolution output has shape (N_bins, N_types), all values are float and no entry is Nan.

**[schema / validation check]** Every (array_row, array_col) pair appears exactly once in coordinates.csv, and um coordinates agree with indices and square size, meaning the grid is complete.

**[property check]** There must be binning consistency, meaning the four 8 um bins that tile a 16 um bin sum to it exactly, gene by gene. 

**[smoke test]** The program runs end to end on its current input and writes its outputs.

**[reproducibility test]** A teammate who has never run this project can create the environment from environment.yml, install the package with pip install -e ., and get a clean pytest run without installing anything else by hand.

**[schema/validation check]** The program refuses to run if any file under data/raw/ does not match the recorded checksum.

**[reproducibility test]** Deleting results/ and rerunning with the same config and seed reproduces the outputs. 


## First Known Answer - tiny input whose correct output we can state by hand

Input: a 4-cell tissue, 2 genes, 2 cell types.

counts = [[8, 1],   # strong GENE_00 -> type A
          [7, 0],   # strong GENE_00 -> type A
          [0, 9],   # strong GENE_01 -> type B
          [1, 8]]   # strong GENE_01 -> type B

1. `[known-answer test]` For a bin built from equal transcript amounts of two cell types whose cells differ 3-fold in RNA
   content, the estimated fractions are 0.5 / 0.5 (not 0.75 / 0.25).
2. `[property test]` For every bin, on any valid input dataset, the predicted
   fractions are all >= 0 and sum to 1 (within 1e-3).
3. `[metamorphic test]` On the reference dataset at 8 µm, spatial smoothing
   improves domain recovery: ARI(smoothed) > ARI(unsmoothed), and
   ARI(smoothed) > 0.7.


expected composition (by hand):

bins 0 and 1 -> nearly all type A (fraction A ≈ 1.0, fraction B ≈ 0.0)
bins 2 and 3 -> nearly all type B (fraction A ≈ 0.0, fraction B ≈ 1.0)
------
Two genes, two cell types. Type A only expresses gene 1, type B only expresses
gene 2. An A cell has 10 transcripts, a B cell has 30 (RNA content 1 : 3).
Reference signatures (column-normalized): S = [[1, 0], [0, 1]].
Input: one bin with counts y = [30, 30] (30 transcripts from A, 30 from B).
Expected output: fractions A = 0.5, B = 0.5.
(Wrong, un-normalized S = [[10, 0], [0, 30]] would give w = [3, 1] -> 0.75 / 0.25.)
