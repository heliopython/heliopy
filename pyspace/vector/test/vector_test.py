from pyspace.vector.transformations import *


def test_cart2sph():
    x = 1
    y = 0
    z = 0
    r, theta, phi = cart2sph(x, y, z)
    assert r == 1
    assert theta == 0
    assert phi == 0
    print('Hi')


def test_dummy():
    assert 1 == 1
