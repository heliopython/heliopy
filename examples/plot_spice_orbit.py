"""
SPICE orbit plotting
====================

How to plot orbits from SPICE kernels.

In this example we download the Parker Solar Probe SPICE kernel, and plot
its orbit for the first year.
"""


import heliopy.data.spice as spicedata
import heliopy.spice as spice
from datetime import datetime, timedelta
import astropy.units as u
import numpy as np

###############################################################################
# Load the solar orbiter spice kernel. HelioPy will automatically fetch the
# latest kernel
kernels = spicedata.get_kernel('psp')
kernels += spicedata.get_kernel('psp_pred')
spice.furnish(kernels)
psp = spice.Trajectory('SPP')

###############################################################################
# Generate a time for every day between starttime and endtime
starttime = datetime(2018, 8, 14)
endtime = starttime + timedelta(days=365)
times = []
while starttime < endtime:
    times.append(starttime)
    starttime += timedelta(hours=6)

###############################################################################
# Generate positions
psp.generate_positions(times, 'Sun', 'ECLIPJ2000')
psp.change_units(u.au)

###############################################################################
# Plot the orbit. The orbit is plotted in 3D
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from astropy.visualization import quantity_support
quantity_support()

# Generate a set of timestamps to color the orbits by
times_float = [(t - psp.times[0]).total_seconds() for t in psp.times]
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
kwargs = {'s': 3, 'c': times_float}
ax.scatter(psp.x, psp.y, psp.z, **kwargs)
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_zlim(-1, 1)

###############################################################################
# Plot radial distance and elevation as a function of time
elevation = np.rad2deg(np.arcsin(psp.z / psp.r))

fig, axs = plt.subplots(3, 1, sharex=True)
axs[0].plot(psp.times, psp.r)
axs[0].set_ylim(0, 1.1)
axs[0].set_ylabel('r (AU)')

axs[1].plot(psp.times, elevation)
axs[1].set_ylabel('Elevation (deg)')

axs[2].plot(psp.times, psp.speed)
axs[2].set_ylabel('Speed (km/s)')

plt.show()
