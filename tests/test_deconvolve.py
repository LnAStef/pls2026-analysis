import hashlib, json
import numpy as np
import pandas as pd
from spatial_decode.deconvolve import deconvolve

# Tiny fixed input — 2 bins, 2 genes, 2 cell types
S_tiny = pd.DataFrame({
    "A": [8.0, 1.0],
    "B": [1.0, 8.0]
}, index=["GENE_1", "GENE_2"])

binned_tiny = pd.DataFrame({
    "GENE_1": [8, 1],
    "GENE_2": [1, 8]
}, index=["bin_0", "bin_1"])

# Golden hash — committed, never change by accident
GOLDEN = "26f6c2fcd219cf927dd6df947a1492c3f5e6641b869d425de1a7b52c49fe4098"

def test_deconvolve_characterization():
    result = deconvolve(S_tiny, binned_tiny)
    digest = hashlib.sha256(
        json.dumps([r.tolist() for r in result]).encode()
    ).hexdigest()
    assert digest == GOLDEN, f"deconvolve output changed: {digest}"

def test_deconvolve_known_answer():
    result = deconvolve(S_tiny, binned_tiny)
    assert np.allclose(result[0], [1., 0.], atol=1e-6)
    assert np.allclose(result[1], [0., 1.], atol=1e-6)