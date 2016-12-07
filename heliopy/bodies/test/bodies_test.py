import numpy as np

import heliopy.bodies.sun as sun


def test_rotationrate():
    lat_rand = np.random.rand() * np.pi / 2
    assert sun.rotationrate(lat_rand) < sun.rotationrate(0)
    assert sun.rotationrate(lat_rand) == sun.rotationrate(-lat_rand)
