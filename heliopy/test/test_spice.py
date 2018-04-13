import heliopy.data.spice as spicedata
from datetime import datetime, timedelta
import numpy as np
import pytest

try:
    import spiceypy
    import heliopy.spice as spice
    has_spice = True
except ModuleNotFoundError:
    has_spice = False


@pytest.mark.skipif(not has_spice, reason='Importing spice module failed')
def test_spice():
    orbiter_kernel = spicedata.get_kernel('solo_2020')
    spice.furnish(orbiter_kernel)
    orbiter = spice.Trajectory('Solar Orbiter')

    # Generate 1000 days of data
    starttime = datetime(2020, 3, 1)
    times = [starttime + n * timedelta(days=1) for n in range(1000)]

    orbiter.generate_positions(times, 'Sun', 'ECLIPJ2000')
    assert orbiter.times == times

    # Check it works with numpy arrays too
    times = np.array(times)
    orbiter.generate_positions(times, 'Sun', 'ECLIPJ2000')
