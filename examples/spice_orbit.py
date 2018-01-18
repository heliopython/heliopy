"""
SPICE orbit plotting
====================

How to plot orbits from SPICE kernels.

In this example we download the Solar Orbiter SPICE kernel, and plot it's orbit
from 2020 to 2028.
"""


import heliopy.data.spice as spicedata
import heliopy.spice as spice
from datetime import datetime
import astropy.units as u
import numpy as np

###############################################################################
# Load the solar orbiter spice kernel. HelioPy will automatically fetch the
# latest kernel
orbiter_kernel = spicedata.get_kernel('solar orbiter 2020')
spice.furnish(orbiter_kernel)
orbiter = spice.Trajectory('Solar Orbiter')

###############################################################################
# Choose a starttime, endtime, and the number of points on the orbit to
# generate.
starttime = datetime(2020, 3, 1)
endtime = datetime(2028, 1, 1)
nsteps = 1000

###############################################################################
# Generate positions
orbiter.generate_positions(starttime, endtime, nsteps, 'Sun', 'ECLIPJ2000')
orbiter.change_units(u.au)

###############################################################################
# Plot the orbit. The orbit is plotted in 3D
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from astropy.visualization import quantity_support
quantity_support()

# Generate a set of timestamps to color the orbits by
times_float = [(t - orbiter.times[0]).total_seconds() for t in orbiter.times]
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
kwargs = {'s': 3, 'c': times_float}
ax.scatter(orbiter.x, orbiter.y, orbiter.z, **kwargs)
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_zlim(-1, 1)

###############################################################################
# Plot radial distance and elevation as a function of time
elevation = np.rad2deg(np.arcsin(orbiter.z / orbiter.r))

fig, axs = plt.subplots(2, 1, sharex=True)
axs[0].plot(orbiter.times, orbiter.r)
axs[0].set_ylim(0, 1.1)
axs[0].set_ylabel('r (AU)')

axs[1].plot(orbiter.times, elevation)
axs[1].set_ylabel('Elevation (deg)')

plt.show()
