import datetime

import astropy.units as u
import numpy as np
import pytest
import sunpy.coordinates.sun
from astropy.coordinates import Latitude
from astropy.time import Time
from astropy.utils.exceptions import ErfaWarning

import heliopy.data.spice as spicedata
import heliopy.spice as spice


@pytest.fixture
def solo_trajectory():
    orbiter_kernel = spicedata.get_kernel('helios1')
    spice.furnish(orbiter_kernel)
    return spice.Trajectory('Helios 1')


@pytest.fixture
def times():
    starttime = datetime.datetime(1975, 3, 1)
    return [starttime + n * datetime.timedelta(days=1) for n in range(1000)]


def test_spice(solo_trajectory, times):
    solo_trajectory.generate_positions(times, 'Sun', 'ECLIPJ2000')
    assert (solo_trajectory.times == Time(times)).all()

    # Check it works with numpy arrays too
    times = np.array(times)
    solo_trajectory.generate_positions(times, 'Sun', 'ECLIPJ2000')


def test_coords(solo_trajectory, times):
    solo_trajectory.generate_positions(times, 'Sun', 'IAU_SUN')
    solo_trajectory.coords

    solo_trajectory.generate_positions(times, 'Sun', 'ECLIPJ2000')
    with pytest.raises(ValueError):
        solo_trajectory.coords


def test_body_creation():
    # Test creating by name
    body = spice.Body('Sun')
    assert body.name == 'Sun'
    assert body.id == 10

    # Test creating by ID
    body = spice.Body(10)
    assert body.name == 'SUN'
    assert body.id == 10


def test_invalid_body_creation():
    with pytest.raises(ValueError,
                       match='Body name "Not a body" not known by SPICE'):
        body = spice.Body('Not a body')

    with pytest.raises(ValueError,
                       match='id "104857" not known by SPICE'):
        body = spice.Body(104857)

    with pytest.raises(ValueError,
                       match="body must be an int or str"):
        body = spice.Body(1.0)


def test_body_eq():
    assert spice.Body('Sun') == spice.Body(10)
    assert spice.Body(1) != spice.Body(10)


def test_body_repr():
    assert 'Sun' in spice.Body('Sun').__repr__()
    assert '10' in spice.Body('Sun').__repr__()


def test_kernel():
    kernel = spicedata.get_kernel('helios1')[0]
    solo = spice.Body('helios 1')
    assert len(kernel.bodies) == 1
    assert kernel.bodies[0] == solo

    assert kernel.coverage(solo) == [
        datetime.datetime(1974, 12, 10, 23, 50, 1, 662,
                          tzinfo=datetime.timezone.utc),
        datetime.datetime(1981, 9, 30, 1, 29, 54, 1651,
                          tzinfo=datetime.timezone.utc)
    ]


# Global atol and rtol for comparing coordinates
_tols = {'atol': 1e-6 * u.deg, 'rtol': 0}


def test_spice_sunpy_equivalence():
    # Check that SPICE coordinates and the sunpy coordinates we associate
    # with those coordinates are the same
    t = ['1992-12-21']
    b0 = Latitude(sunpy.coordinates.sun.B0(t))
    l0 = sunpy.coordinates.sun.L0(t, light_travel_time_correction=False)

    earth = spice.Trajectory('Earth')
    earth.generate_positions(t, 'Sun', 'IAU_SUN')

    assert u.allclose(earth.coords.lon, l0, **_tols)
    assert u.allclose(earth.coords.lat, b0, **_tols)


def test_coord_err():
    t = ['1992-12-21']
    earth = spice.Trajectory('Earth')
    earth.generate_positions(t, 'Sun', 'IAU_SUN', abcorr='LT')
    with pytest.raises(NotImplementedError):
        earth.coords
