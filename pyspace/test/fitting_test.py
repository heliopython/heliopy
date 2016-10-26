from pyspace.fitting import *
import numpy as np


def test_maxwellian():
    A = np.random.rand()
    sigma = np.random.rand()
    assert maxwellian(0, A, 0, sigma) == A

    mu = np.random.rand()
    assert maxwellian(mu, A, mu, sigma) == A
