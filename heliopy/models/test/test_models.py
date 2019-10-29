import astropy.units as u
from astropy.tests.helper import assert_quantity_allclose
from heliopy.models import ParkerSpiral


def test_parker_spiral():
    spiral = ParkerSpiral(100 * u.km / u.s, 0 * u.au, 0 * u.deg)
    longs = spiral.longitude([1, 2] * u.au)
    assert_quantity_allclose(longs[0], -254.7492444 * u.deg)
    assert_quantity_allclose(longs[1], -509.4984888 * u.deg)
