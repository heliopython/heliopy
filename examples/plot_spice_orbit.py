"""
SPICE orbit plotting
====================

How to plot orbits from SPICE kernels.

In this example we download the Parker Solar Probe SPICE kernel, and plot
its orbit for the first year.
"""


from datetime import datetime, timedelta

import astropy.units as u
import numpy as np

import heliopy.data.spice as spicedata
import heliopy.spice as spice

###############################################################################
# Load the solar orbiter spice kernel. heliopy will automatically fetch and
# load the latest kernel
spicedata.get_kernel('psp')
spicedata.get_kernel('psp_pred')
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
from astropy.visualization import quantity_support
from mpl_toolkits.mplot3d import Axes3D

quantity_support()

# Generate a set of timestamps to color the orbits by
times_float = (psp.times - psp.times[0]).value
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
kwargs = {'s': 3, 'c': times_float}
ax.scatter(psp.x, psp.y, psp.z, **kwargs)
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_zlim(-1, 1)

###############################################################################
# Plot radial distance and elevation as a function of time
plot_times = psp.times.to_datetime()
elevation = np.rad2deg(np.arcsin(psp.z / psp.r))

fig, axs = plt.subplots(3, 1, sharex=True)
axs[0].plot(plot_times, psp.r)
axs[0].set_ylim(0, 1.1)
axs[0].set_ylabel('r (AU)')

axs[1].plot(plot_times, elevation)
axs[1].set_ylabel('Elevation (deg)')

axs[2].plot(plot_times, psp.speed)
axs[2].set_ylabel('Speed (km/s)')

plt.show()
