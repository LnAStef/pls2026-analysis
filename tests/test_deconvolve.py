import warnings
import hashlib
import json

import numpy as np
import pandas as pd
import pytest

from spatial_decode.deconvolve import deconvolve

# Tiny fixed input: 2 bins, 2 genes, 2 cell types
S_tiny = pd.DataFrame({"A": [8.0, 1.0], "B": [1.0, 8.0]}, index=["GENE_1", "GENE_2"])
binned_tiny = pd.DataFrame(
    {"GENE_1": [8, 1], "GENE_2": [1, 8]}, index=["bin_0", "bin_1"]
)

# Golden hash: committed, never change by accident
GOLDEN = "26f6c2fcd219cf927dd6df947a1492c3f5e6641b869d425de1a7b52c49fe4098"


def test_deconvolve_characterization():
    result = deconvolve(S_tiny, binned_tiny)
    digest = hashlib.sha256(json.dumps(result.to_numpy().tolist()).encode()).hexdigest()
    assert digest == GOLDEN, f"deconvolve output changed: {digest}"


def test_deconvolve_known_answer():
    result = deconvolve(S_tiny, binned_tiny)
    assert np.allclose(result.loc["bin_0"], [1.0, 0.0], atol=1e-6)
    assert np.allclose(result.loc["bin_1"], [0.0, 1.0], atol=1e-6)


def test_deconvolve_is_labelled():
    result = deconvolve(S_tiny, binned_tiny)
    assert list(result.columns) == ["A", "B"]
    assert list(result.index) == ["bin_0", "bin_1"]


def test_deconvolve_ignores_gene_order():
    shuffled = binned_tiny[["GENE_2", "GENE_1"]]
    pd.testing.assert_frame_equal(
        deconvolve(S_tiny, binned_tiny), deconvolve(S_tiny, shuffled)
    )

def test_deconvolve_normalises_columns_not_rows():
    """S is deliberately asymmetric: row sums differ from column sums."""
    S = pd.DataFrame({"A": [3.0, 1.0], "B": [1.0, 1.0]}, index=["g1", "g2"])
    # y = 4 * (A's profile [0.75, 0.25]) + 2 * (B's profile [0.5, 0.5]) = [4, 2]
    y = pd.DataFrame({"g1": [4], "g2": [2]}, index=["bin"])
    result = deconvolve(S, y)
    assert np.allclose(result.loc["bin"], [2 / 3, 1 / 3])


def test_deconvolve_empty_bin_is_nan_without_warning():
    empty = pd.DataFrame({"GENE_1": [0], "GENE_2": [0]}, index=["bin_empty"])
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # a silent 0/0 would raise RuntimeWarning
        result = deconvolve(S_tiny, empty)
    assert result.isna().all(axis=None)


def test_deconvolve_fractions_ignore_total_depth():
    """Metamorphic: doubling every count must not change the fractions."""
    doubled = binned_tiny * 2
    pd.testing.assert_frame_equal(
        deconvolve(S_tiny, binned_tiny), deconvolve(S_tiny, doubled), atol=1e-9
    )


@pytest.mark.parametrize("scale", [1, 3, 50])
def test_deconvolve_fractions_are_valid(scale):
    """Property: every non-empty bin has fractions >= 0 that sum to 1."""
    result = deconvolve(S_tiny, binned_tiny * scale)
    assert (result.to_numpy() >= 0).all()
    assert np.allclose(result.sum(axis=1), 1.0)


def test_deconvolve_rejects_mismatched_genes():
    wrong = binned_tiny.rename(columns={"GENE_1": "OTHER"})
    with pytest.raises(ValueError, match="gene names"):
        deconvolve(S_tiny, wrong)

def test_deconvolve_units_are_transcripts_not_cells():
    """Equal transcript amounts from types with 1:3 RNA content give 0.5 / 0.5."""
    S = pd.DataFrame({"A": [10.0, 0.0], "B": [0.0, 30.0]}, index=["g1", "g2"])
    y = pd.DataFrame({"g1": [30], "g2": [30]}, index=["bin"])
    result = deconvolve(S, y)
    assert np.allclose(result.loc["bin"], [0.5, 0.5])
