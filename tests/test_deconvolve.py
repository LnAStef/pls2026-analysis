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


def test_deconvolve_empty_bin_is_nan():
    empty = pd.DataFrame({"GENE_1": [0], "GENE_2": [0]}, index=["bin_empty"])
    assert deconvolve(S_tiny, empty).isna().all(axis=None)


def test_deconvolve_rejects_mismatched_genes():
    wrong = binned_tiny.rename(columns={"GENE_1": "OTHER"})
    with pytest.raises(ValueError):
        deconvolve(S_tiny, wrong)