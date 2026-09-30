# <project name> spatial-decode

## What it does

SpatialDecode takes a spatial transcriptomics dataset (counts per 2 µm², coordinates, and a single-cell reference) and can answer the following questions:
Which fraction of each bin's transcripts comes from which cell type (deconvolution) and to which spatial domain each bin belongs. It then compares its own answers with the simulator's ground truth. The deconvolution/domain method is tested and correct results are obtained before it is applied to real data.


## Inputs

SpatialDecode takes a spatial transcriptomics dataset (counts per 2 µm², coordinates, and a single-cell reference) and can answer the following questions:
Which fraction of each bin's transcripts comes from which cell type (deconvolution) and to which spatial domain each bin belongs. It then compares its own answers with the simulator's ground truth. The deconvolution/domain method is tested and correct results are obtained before it is applied to real data.

## Outputs

A `results_<name>/` directory (Data Contract §4):
- `predicted_composition.csv` (bin_id, cell_type, fraction)
- `predicted_domains.csv` (bin_id, domain)
- `run_metadata.json` (contract version, tool version, parameters, bin_size_um)
plus scores: RMSE and Jensen–Shannon divergence (composition), ARI (domains).


## Acceptance criteria

Concrete, checkable statements of "how we will know it is right". Tag each with the kind of
check that enforces it (smoke, known-answer, property, metamorphic, characterization,
schema/validation, reproducibility).

1. `[known-answer test]` For a bin built from equal transcript amounts of two cell types whose cells differ 3-fold in RNA
   content, the estimated fractions are 0.5 / 0.5 (not 0.75 / 0.25).
2. `[property test]` For every bin, on any valid input dataset, the predicted
   fractions are all >= 0 and sum to 1 (within 1e-3).
3. `[metamorphic test]` On the reference dataset at 8 µm, spatial smoothing
   improves domain recovery: ARI(smoothed) > ARI(unsmoothed), and
   ARI(smoothed) > 0.7.


## First known answer

Two genes, two cell types. Type A only expresses gene 1, type B only expresses
gene 2. An A cell has 10 transcripts, a B cell has 30 (RNA content 1 : 3).
Reference signatures (column-normalized): S = [[1, 0], [0, 1]].
Input: one bin with counts y = [30, 30] (30 transcripts from A, 30 from B).
Expected output: fractions A = 0.5, B = 0.5.
(Wrong, un-normalized S = [[10, 0], [0, 30]] would give w = [3, 1] -> 0.75 / 0.25.)
