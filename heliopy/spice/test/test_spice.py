import heliopy.spice as spice
import heliopy.data.spice as spicedata
from datetime import datetime
import astropy.units as u


def test_spice():
    orbiter_kernel = spicedata.get_kernel('solar orbiter 2020')
    orbiter = spice.SpiceKernel('Solar Orbiter', orbiter_kernel)

    starttime = datetime(2020, 3, 1)
    endtime = datetime(2028, 1, 1)
    nsteps = 1000

    orbiter.generate_positions(starttime, endtime, nsteps, 'Sun', 'ECLIPJ2000')
    orbiter.positions = orbiter.positions.to(u.au)
