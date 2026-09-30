# <project name> — specification

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

1. `metamorphic` The ARI(smoothed) must be >= the ARI(unsmoothed) (= better domain clustering after smoothing).
2. `known-answer` The sum of four 8 um bins is = sum of their 16 um bin.
3. `known-answer` Better performance than shuffled-label and uniform-composition baseline.

## First known answer

Input: I do not understand.
Expected output: see above
