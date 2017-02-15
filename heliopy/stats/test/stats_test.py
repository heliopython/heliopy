from heliopy.stats.stats import *
from heliopy.stats.distributions import *
from heliopy.stats.fitting import *
import numpy as np


class TestFitting():
    def test_bin_2d_data(self):
        x = [0.5, 1.5, 1.5, 2.5]
        y = [0.5, 0.5, 2.5, 1.5]
        hist, xedges, yedges, xbins, ybins = bin_2d_data(x, y,
                                                         bins=3, normed=False)
        hist_expected = np.array([[1, 1, 0],
                                  [0, 0, 1],
                                  [0, 1, 0]])
        np.testing.assert_equal(hist, hist_expected)
        np.testing.assert_equal(((xedges[:-1] + xedges[1:]) / 2), xbins[1, :])
        np.testing.assert_equal(((yedges[:-1] + yedges[1:]) / 2), ybins[:, 1])


def test_hist():
    x = np.array([1, 2, 2, 3])
    out, bins = hist(x, bins=3, return_centres=True)

    np.testing.assert_almost_equal(out, np.array([0.375, 0.75, 0.375]))
    np.testing.assert_almost_equal(bins, np.array([4 / 3, 6 / 3, 8 / 3]))


def test_binmean():
    x = np.array([1.5, 1.5, 2.5, 2.6, 3.5])
    y = np.array([1, 3, 6, 8, 10])
    bins = np.array([1, 2, 3, 4])
    out = binmean(x, y, bins)
    expected = np.array([2, 7, 10])
    np.testing.assert_almost_equal(out, expected)


def test_kent_dist():
    theta = np.linspace(-np.pi / 2, np.pi / 2, 50)
    phi = np.linspace(-np.pi, np.pi, 100)
    theta, phi = np.meshgrid(theta, phi)

    # Simple distribution centred on an arbitrary point
    phi_0 = 1.2
    theta_0 = 0.2
    theta_1 = 0.5
    phi_1 = 0.5
    kappa = 4
    beta = 1
    dist = kent_dist(theta, phi, kappa, beta,
                     theta_0, phi_0, theta_1, phi_1)
    # Divide by cos(theta) to remove spherical area dependence
    dist /= np.cos(theta)
    dist_max = np.argmax(dist)
    # Check that maximum is closest to r_0
    expected_max = np.argmin((theta - theta_0)**2 + (phi - phi_0)**2)
    np.testing.assert_equal(dist_max, expected_max)
