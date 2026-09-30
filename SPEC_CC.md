# <project name> — specification

## What it does
## The analysis tool takes simulated spatial transcriptomics data and tries to reconstruct the underlying biological structure without seeing the correct answer. In practice, it:
##1. checks that the input dataset follows the agreed data contract;
##2. combines the very sparse 2 µm squares into larger analysis bins chosen by the user;
##3. uses the provided single-cell reference data to learn the expression patterns of the different cell types;
##4. estimates which cell types contributed to each spatial bin and in what proportions;
##5. assigns the spatial bins to spatial domains/regions.
##An important principle is that the analysis tool cannot use the ground_truth/ folder while making its predictions. Ground truth is only used afterwards to evaluate how accurate the predictions were.

<One paragraph in your own words.>

## Inputs

<What it reads. Refer to the Data Contract rather than inventing a format.>
## spatial gene counts + spatial coordinates + a labelled single-cell reference → analysis

## Outputs
##predicted cell-type fractions + predicted spatial domains + analysis settings

## Acceptance criteria

Concrete, checkable statements of "how we will know it is right". Tag each with the kind of
check that enforces it (smoke, known-answer, property, metamorphic, characterization,
schema/validation, reproducibility).

# 3 acceptance criteria ex:
# Count validation acceptance criteria = it proves there are no negative integer counts (property test check)

def check_counts_valid(counts):
    assert(sum(counts.ravel() < 0) == 0)  # TODO: assert non-negative integers, then return True
    assert (sum(counts.ravel() %1!=0)==0)
    return True

print(check_counts_valid(counts))

# Metamorphic test: bin sizes act as expected (true composition is purer at smaller bins, while estimates are noisier)

# Known answer test: binning is exact (sum of 4 8um squares make up a 16um square)

## First known answer

Input: <the smallest input whose correct output you can state by hand>
Expected output: <what a correct program must produce for it>
