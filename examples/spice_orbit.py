import heliopy.data.spice as spicedata
import heliopy.spice as spice
from datetime import datetime
import astropy.units as u

###############################################################################
# Load the solar orbiter spice kernel. HelioPy will automatically fetch the
# latest kernel
orbiter_kernel = spicedata.get_kernel('solar orbiter 2020')
orbiter = spice.SpiceKernel('Solar Orbiter', orbiter_kernel)

###############################################################################
# Choose a starttime, endtime, and the number of points on the orbit to
# generate.
starttime = datetime(2020, 3, 1)
endtime = datetime(2028, 1, 1)
nsteps = 1000

###############################################################################
# Generate positions
orbiter.generate_positions(starttime, endtime, nsteps, 'Sun', 'ECLIPJ2000')
orbiter.positions = orbiter.positions.to(u.au)

###############################################################################
# Plot the orbit
import matplotlib.pyplot as plt
from astropy.visualization import quantity_support
quantity_support

# Generate a set of timestamps to color the orbits by
times = [(t - orbiter.times[0]).total_seconds() for t in orbiter.times]
fig, axs = plt.subplots(2, 2, sharex=True)
kwargs = {'s': 3, 'c': times}
axs[0, 0].scatter(orbiter.positions[:, 0], orbiter.positions[:, 1], **kwargs)
axs[1, 0].scatter(orbiter.positions[:, 0], orbiter.positions[:, 2], **kwargs)
axs[1, 1].scatter(orbiter.positions[:, 1], orbiter.positions[:, 2], **kwargs)

for ax in axs.ravel():
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
plt.show()
