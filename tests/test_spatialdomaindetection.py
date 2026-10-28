"""Checks for spatial-domain detection (spec §3.4, §6)."""

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import adjusted_rand_score

from spatial_decode.cluster import (
    UNASSIGNED,
    cluster_domains,
    composition_to_grid,
    detect_domains,
    labels_to_frame,
    smooth_composition,
)

SEED = 0
N_INIT = 5


def noisy_three_domain_grid(noise, seed=1, size=30):
    """Three vertical stripes with a different cell-type mixture each, plus Dirichlet noise."""
    rng = np.random.default_rng(seed)
    means = np.array([[0.8, 0.1, 0.1], [0.1, 0.8, 0.1], [0.1, 0.1, 0.8]])
    truth = np.repeat(np.arange(3), size // 3)[None, :].repeat(size, axis=0)
    comp = np.empty((size, size, 3))
    for r in range(size):
        for c in range(size):
            comp[r, c] = rng.dirichlet(means[truth[r, c]] * noise)
    return comp, truth


# --- smoothing ------------------------------------------------------------------------
def test_constant_grid_is_unchanged_by_smoothing():
    comp = np.tile([0.2, 0.3, 0.5], (6, 7, 1))
    assert np.allclose(smooth_composition(comp, radius=2), comp)


def test_single_outlier_is_spread_over_its_window():
    comp = np.tile([1.0, 0.0], (5, 5, 1))
    comp[2, 2] = [0.0, 1.0]
    out = smooth_composition(comp, radius=1)
    assert out[2, 2, 1] == pytest.approx(1 / 9)  # centre: 1 of 9 bins is the outlier
    assert out[1, 1, 1] == pytest.approx(1 / 9)  # neighbour sees it too
    assert out[0, 0, 1] == pytest.approx(0.0)  # outside the window


def test_border_averages_only_existing_neighbours():
    comp = np.zeros((3, 3, 2))
    comp[..., 0] = np.arange(9).reshape(3, 3) / 8
    comp[..., 1] = 1 - comp[..., 0]
    out = smooth_composition(comp, radius=1)
    # corner (0,0) has 4 existing bins in its window: (0,0),(0,1),(1,0),(1,1)
    assert out[0, 0, 0] == pytest.approx(comp[:2, :2, 0].mean())


def test_empty_bins_do_not_dilute_neighbours():
    comp = np.tile([0.5, 0.5], (3, 3, 1))
    comp[1, 1] = np.nan
    out = smooth_composition(comp, radius=1)
    assert np.allclose(out, 0.5)  # a zero-filled average would give < 0.5 near the hole


def test_isolated_empty_bin_stays_nan():
    comp = np.full((5, 5, 2), np.nan)
    comp[0, 0] = [1.0, 0.0]
    out = smooth_composition(comp, radius=1)
    assert np.isnan(out[4, 4]).all()


@pytest.mark.parametrize("radius", [0, 1, 3])
def test_smoothed_fractions_are_valid(radius):
    comp, _ = noisy_three_domain_grid(noise=10)
    out = smooth_composition(comp, radius)
    assert (out >= 0).all()
    assert np.allclose(out.sum(axis=-1), 1.0)


def test_negative_radius_is_rejected():
    with pytest.raises(ValueError):
        smooth_composition(np.ones((3, 3, 2)) / 2, radius=-1)


# --- clustering -----------------------------------------------------------------------
def test_smoothing_improves_ari_on_noisy_data():
    comp, truth = noisy_three_domain_grid(noise=6)
    smoothed, unsmoothed = detect_domains(comp, 3, radius=2, seed=SEED, n_init=N_INIT)
    ari_smooth = adjusted_rand_score(truth.ravel(), smoothed.ravel())
    ari_raw = adjusted_rand_score(truth.ravel(), unsmoothed.ravel())
    assert ari_smooth >= ari_raw
    assert ari_smooth > 0.9


def test_clustering_is_deterministic():
    comp, _ = noisy_three_domain_grid(noise=6)
    a = cluster_domains(comp, 3, SEED, N_INIT)
    b = cluster_domains(comp, 3, SEED, N_INIT)
    assert np.array_equal(a, b)


def test_empty_bins_are_unassigned_not_clustered():
    comp, _ = noisy_three_domain_grid(noise=20)
    comp[0, 0] = np.nan
    labels = cluster_domains(comp, 3, SEED, N_INIT)
    assert labels[0, 0] == UNASSIGNED
    assert (labels[1:, 1:] >= 0).all()


# --- table conversion -----------------------------------------------------------------
def test_long_table_round_trip_and_ids():
    frame = pd.DataFrame(
        {
            "bin_id": ["bin_r0_c0", "bin_r0_c0", "bin_r1_c1", "bin_r1_c1"],
            "cell_type": ["A", "B", "A", "B"],
            "fraction": [0.25, 0.75, 1.0, 0.0],
        }
    )
    grid, types = composition_to_grid(frame, 2, 2)
    assert types == ["A", "B"]
    assert np.allclose(grid[0, 0], [0.25, 0.75])
    assert np.isnan(grid[0, 1]).all()  # not listed = empty
    out = labels_to_frame(np.array([[0, 1], [1, 2]]))
    assert list(out.columns) == ["bin_id", "domain"]
    assert out["bin_id"].tolist() == [
        "bin_r0_c0",
        "bin_r0_c1",
        "bin_r1_c0",
        "bin_r1_c1",
    ]
