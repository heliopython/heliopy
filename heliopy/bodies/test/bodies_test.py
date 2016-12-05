import numpy as np

import heliopy.bodies.sun as sun


def test_rotationrate():
    lat_rand = np.random.rand() * np.pi / 2
    assert rotationrate(lat_rand) < rotationrate(0)
    assert rotationrate(lat_rand) == rotationrate(-lat_rand)
