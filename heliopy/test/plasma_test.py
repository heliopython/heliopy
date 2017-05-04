from heliopy.plasma import *
import heliopy.constants as const
import numpy as np


def test_magneticpressure():
    assert magneticpressure(0) == 0

    out = magneticpressure(1e9)
    expected = 1 / (2 * const.mu_0)
    np.testing.assert_almost_equal(out, expected)


def test_vth2temp():
    out = vth2temp(1e-3, 1)
    expected = 1 / (2 *const.k_B)
    np.testing.assert_almost_equal(out, expected)


def test_temp2vth():
    out = temp2vth(vth2temp(1234, 4321), 4321)
    np.testing.assert_almost_equal(out, 1234)


def test_alfvenspeed():
    out = alfvenspeed(1e-6, 1e9)
    expected = 1e-3 / np.sqrt(const.m_p * const.mu_0)
    np.testing.assert_almost_equal(out, expected)
