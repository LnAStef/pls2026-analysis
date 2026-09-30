# pls2026-analysis — specification

## What it does

The project builds a program that takes spatial-transcriptomics data, bins it, estimates 
the cell-type composition (deconvolution) of each bin and partitions into spatial domains and measures 
how close it is to simulators truth. 

## Inputs

1. metadata.json (format version, square size, provenance)
2. coordinates.csv (position of each square on the grid)
3. counts.csv (squares x genes count matrix)
4. reference_counts.csv (counts for individually profiled cells)
5. reference_labesl.csv (the cell type of each reference cell)

## Outputs

The output of the analysis track are the following three files:
1. predicted_composition.csv (bin_id, cell_type, fraction)
2. predicte_domains.csv (bin_id, domain) 
3. run_metadata.json (contract version consumed, tool version, parameters, bin_size_um used)


## Acceptance criteria

1. `[Known-answer test]` 
2. `[check type]` <criterion>
3. `[Property test]` Predicted fractions are per bin and sum to 1.

## First known answer

Input: Count fractions
Expected output: Predicted fractions are per bin and sum to 1