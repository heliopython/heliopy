"""
SPICE orbit plotting
====================

How to plot Casini orbits from SPICE kernels.

In this example we download the Cassini Spacecraft SPICE kernel, and plot
its orbit around Saturn for the first year.
"""


import heliopy.data.spice as spicedata
import heliopy.spice as spice
from datetime import datetime, timedelta
import astropy.units as u
import numpy as np

###############################################################################
# Load the solar orbiter spice kernel. HelioPy will automatically fetch the
# latest kernel
kernels = spicedata.get_kernel('cassini_test')
spice.furnish(kernels)
cassini = spice.Trajectory('cassini')

###############################################################################
# Generate a time for every day between starttime and endtime
starttime = datetime(2004, 7, 2)
endtime = starttime + timedelta(days=365)
times = []
while starttime < endtime:
    times.append(starttime)
    starttime += timedelta(hours=6)

###############################################################################
# Generate positions
cassini.generate_positions(times, 'Saturn', 'ECLIPJ2000')
cassini.change_units(u.km)

###############################################################################
# Plot the orbit. The orbit is plotted in 3D
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from astropy.visualization import quantity_support
quantity_support()

# Generate a set of timestamps to color the orbits by
times_float = (cassini.times - cassini.times[0]).value
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
kwargs = {'s': 3, 'c': times_float}
ax.scatter(cassini.x, cassini.y, cassini.z, **kwargs)

###############################################################################
# Plot radial distance and elevation as a function of time
plot_times = cassini.times.to_datetime()
elevation = np.rad2deg(np.arcsin(cassini.z / cassini.r))

fig, axs = plt.subplots(3, 1, sharex=True)
axs[0].plot(plot_times, cassini.r)
axs[0].set_ylabel('r (km)')

axs[1].plot(plot_times, elevation)
axs[1].set_ylabel('Elevation (deg)')

axs[2].plot(plot_times, cassini.speed)
axs[2].set_ylabel('Speed (km/s)')

plt.show()
