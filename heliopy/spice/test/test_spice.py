import datetime

from astropy.time import Time
from astropy.utils.exceptions import ErfaWarning
import numpy as np
import pytest

import heliopy.spice as spice
import heliopy.data.spice as spicedata

spice.setup_spice()


@pytest.fixture
def solo_trajectory():
    orbiter_kernel = spicedata.get_kernel('solo')
    spice.furnish(orbiter_kernel)
    return spice.Trajectory('Solar Orbiter')


@pytest.fixture
def times():
    starttime = datetime.datetime(2020, 3, 1)
    return [starttime + n * datetime.timedelta(days=1) for n in range(1000)]


def test_spice(solo_trajectory, times):
    solo_trajectory.generate_positions(times, 'Sun', 'ECLIPJ2000')
    assert (solo_trajectory.times == Time(times)).all()

    # Check it works with numpy arrays too
    times = np.array(times)
    solo_trajectory.generate_positions(times, 'Sun', 'ECLIPJ2000')


def test_coords(solo_trajectory, times):
    # Smoke test that coords work

    # Catch ErfaWarnings for dates long in the future
    solo_trajectory.generate_positions(times, 'Sun', 'J2000')
    solo_trajectory.coords

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
    kernel = spicedata.get_kernel('solo')[0]
    solo = spice.Body('solar orbiter')
    assert len(kernel.bodies) == 1
    assert kernel.bodies[0] == solo

    assert kernel.coverage(solo) == [
        datetime.datetime(2020, 2, 10, 4, 55, 49, 670002,
                          tzinfo=datetime.timezone.utc),
        datetime.datetime(2030, 11, 18, 19, 7, 39, 363433,
                          tzinfo=datetime.timezone.utc)
    ]
