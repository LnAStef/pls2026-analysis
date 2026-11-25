import pandas as pd
import pytest
import numpy as np
from spatial_decode.scoring import score, score_composition


def test_perfect_prediction_gets_perfect_scores():
    """A perfect prediction should have RMSE=0, JSD=0, and ARI=1."""
    coordinates = pd.DataFrame(
        {
            "square_id": [
                "sq_r0_c0",
                "sq_r0_c1",
                "sq_r0_c2",
                "sq_r0_c3",
            ],
            "array_row": [0, 0, 0, 0],
            "array_col": [0, 1, 2, 3],
        }
    )

    # Ground truth is stored as transcript counts per square.
    #
    # The first two squares form bin_r0_c0:
    #     A = 100, B = 1
    #
    # The second two form bin_r0_c1:
    #     A = 1, B = 100
    truth_composition = pd.DataFrame(
        {
            "square_id": [
                "sq_r0_c0",
                "sq_r0_c1",
                "sq_r0_c2",
                "sq_r0_c3",
            ],
            "cell_type": ["A", "B", "A", "B"],
            "n_transcripts": [100, 1, 1, 100],
        }
    )

    predicted_composition = pd.DataFrame(
        {
            "bin_id": [
                "bin_r0_c0",
                "bin_r0_c0",
                "bin_r0_c1",
                "bin_r0_c1",
            ],
            "cell_type": ["A", "B", "A", "B"],
            "fraction": [
                100 / 101,
                1 / 101,
                1 / 101,
                100 / 101,
            ],
        }
    )

    truth_domains = pd.DataFrame(
        {
            "square_id": [
                "sq_r0_c0",
                "sq_r0_c1",
                "sq_r0_c2",
                "sq_r0_c3",
            ],
            "domain": ["left", "left", "right", "right"],
        }
    )

    # Domain names deliberately differ from the truth.
    # ARI compares grouping, not the literal label names.
    predicted_domains = pd.DataFrame(
        {
            "bin_id": ["bin_r0_c0", "bin_r0_c1"],
            "domain": [0, 1],
        }
    )

    result = score(
        predicted_composition=predicted_composition,
        predicted_domains=predicted_domains,
        truth_composition=truth_composition,
        truth_domains=truth_domains,
        coordinates=coordinates,
        bin_size_um=4,
        square_size_um=2,
    )

    assert result["rmse"] == pytest.approx(0.0)
    assert result["jensen_shannon_divergence"] == pytest.approx(0.0)
    assert result["ari"] == pytest.approx(1.0)


def test_empty_bin_is_nan_and_excluded_from_scoring():
    """A zero-transcript bin stays in the matrix as NaN and does not affect the scores."""
    coordinates = pd.DataFrame(
        {
            "square_id": ["sq_r0_c0", "sq_r0_c1"],
            "array_row": [0, 0],
            "array_col": [0, 1],
        }
    )

    # Only the first square (bin_r0_c0) has transcripts; bin_r0_c1 is empty.
    truth_composition = pd.DataFrame(
        {
            "square_id": ["sq_r0_c0", "sq_r0_c0"],
            "cell_type": ["A", "B"],
            "n_transcripts": [3, 1],
        }
    )

    predicted_composition = pd.DataFrame(
        {
            "bin_id": ["bin_r0_c0", "bin_r0_c0"],
            "cell_type": ["A", "B"],
            "fraction": [0.75, 0.25],
        }
    )

    result = score_composition(
        predicted_composition=predicted_composition,
        truth_composition=truth_composition,
        coordinates=coordinates,
        bin_size_um=2,
        square_size_um=2,
    )

    matrix = result["composition_matrix"]
    assert list(matrix.index) == ["bin_r0_c0", "bin_r0_c1"]
    assert matrix.loc["bin_r0_c1"].isna().all()
    assert matrix.loc["bin_r0_c0", "A"] == pytest.approx(0.75)
    assert result["rmse"] == pytest.approx(0.0)
    assert result["jensen_shannon_divergence"] == pytest.approx(0.0)


def test_composition_rmse_is_global():
    """RMSE must be calculated across all bins and cell types."""
    coordinates = pd.DataFrame(
        {
            "square_id": ["s0", "s1"],
            "array_row": [0, 0],
            "array_col": [0, 1],
        }
    )

    truth_composition = pd.DataFrame(
        {
            "square_id": ["s0", "s1"],
            "cell_type": ["A", "A"],
            "n_transcripts": [100, 100],
        }
    )

    predicted_composition = pd.DataFrame(
        {
            "bin_id": [
                "bin_r0_c0",
                "bin_r0_c0",
                "bin_r0_c1",
                "bin_r0_c1",
            ],
            "cell_type": ["A", "B", "A", "B"],
            "fraction": [1.0, 0.0, 0.0, 1.0],
        }
    )

    scores = score_composition(
        predicted_composition=predicted_composition,
        truth_composition=truth_composition,
        coordinates=coordinates,
        bin_size_um=2.0,
        square_size_um=2.0,
    )

    expected_rmse = np.sqrt(0.5)

    assert scores["rmse"] == pytest.approx(expected_rmse)
