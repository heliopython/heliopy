from datetime import datetime, timedelta

from astropy.time import Time
from astropy.utils.exceptions import ErfaWarning
import numpy as np
import pytest

import heliopy.spice as spice
import heliopy.data.spice as spicedata


@pytest.fixture
def solo_trajectory():
    orbiter_kernel = spicedata.get_kernel('solo_2020')
    spice.furnish(orbiter_kernel)
    return spice.Trajectory('Solar Orbiter')


@pytest.fixture
def times():
    starttime = datetime(2020, 3, 1)
    return [starttime + n * timedelta(days=1) for n in range(1000)]


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
