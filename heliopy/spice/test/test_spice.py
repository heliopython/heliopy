import heliopy.data.spice as spicedata
from datetime import datetime
import astropy.units as u
import pytest

try:
    import spiceypy
    import heliopy.spice as spice
    has_spice = True
except ModuleNotFoundError:
    has_spice = False


@pytest.mark.skipif(not has_spice, reason='Importing spice module failed')
def test_spice():
    orbiter_kernel = spicedata.get_kernel('solar orbiter 2020')
    orbiter = spice.SpiceKernel('Solar Orbiter', orbiter_kernel)

    starttime = datetime(2020, 3, 1)
    endtime = datetime(2028, 1, 1)
    nsteps = 1000

    orbiter.generate_positions(starttime, endtime, nsteps, 'Sun', 'ECLIPJ2000')
    orbiter.positions = orbiter.positions.to(u.au)
