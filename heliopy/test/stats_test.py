from heliopy.stats import *
import numpy as np


def test_maxwellian():
    x = np.array([1, 2, 2, 3])
    out, bins = hist(x, bins=3, return_centres=True)

    np.testing.assert_equal(out, np.array([0.375, 0.75, 0.375]))
    np.testing.assert_almost_equal(bins, np.array([4 / 3, 6 / 3, 8 / 3]))
