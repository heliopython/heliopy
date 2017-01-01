from heliopy.spectra import *
import numpy as np


def test_spectral_slopes():
    x = np.array([1, 2, 3, 4])
    y = x**-0.5
    out = spectral_slopes(x, y, nbins=1)
    np.testing.assert_equal(out[0], [1, 4])
    np.testing.assert_almost_equal(out[1], [-0.5])
