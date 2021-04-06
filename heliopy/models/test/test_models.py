import astropy.units as u
from astropy.tests.helper import assert_quantity_allclose

from heliopy.models import ParkerSpiral


def test_parker_spiral():
    spiral = ParkerSpiral(100 * u.km / u.s, 0 * u.au, 0 * u.deg)
    longs = spiral.longitude([1, 2] * u.au)
    assert_quantity_allclose(longs[0], -254.7492444 * u.deg)
    assert_quantity_allclose(longs[1], -509.4984888 * u.deg)


def test_spiral_rot_rate():
    # Check that a slower rotation rate results in a less wound spiral
    v = 100 * u.km / u.s
    r0 = 0 * u.au
    l0 = 0 * u.deg
    spiral1 = ParkerSpiral(v, r0, l0)
    spiral2 = ParkerSpiral(v, r0, l0, 14 * u.deg / u.day)

    long1 = spiral1.longitude(1 * u.au)
    long2 = spiral1.longitude(2 * u.au)
    assert long1 > long2
