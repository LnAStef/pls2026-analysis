# <project name> spatial-decode

## What it does

The program will take the data of genes in the tissue, provided by the simulation track and will finally give back an estimation of how 
the cell types are spatially distributed in the simulated tissue. To get to this point, the data has to be binned & the cell-types in
each bin have to be determined. Finally, the result should be stored against a ground truth (also provided by the simulation track).

## Inputs

- coordinates.csv = position of each square on the grid
- counts.csv = squares x gene count matrix
- reference / directory = includes reference_counts.csv (individually profiled cells), reference_labels.csv (cell types of reference cells)
  metadata.json (format version, square size and other metadata on the "tissue" and "experiment")

## Outputs

- predicted_composition.csv = includes bin_id, cell_type and fraction
- predicted_domains.csv = contains bin_id and domain
- run_metadata.json = contains contact version consumed, tool version, parameters and bin_size_um used

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
