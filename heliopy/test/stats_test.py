from heliopy.stats import *
import numpy as np


def test_hist():
    x = np.array([1, 2, 2, 3])
    out, bins = hist(x, bins=3, return_centres=True)

    np.testing.assert_equal(out, np.array([0.375, 0.75, 0.375]))
    np.testing.assert_almost_equal(bins, np.array([4 / 3, 6 / 3, 8 / 3]))


def test_binmean():
    x = np.array([1.5, 1.5, 2.5, 2.6, 3.5])
    y = np.array([1, 3, 6, 8, 10])
    bins = np.array([1, 2, 3, 4])
    out = binmean(x, y, bins)
    expected = np.array([2, 7, 10])
    np.testing.assert_almost_equal(out, expected)
