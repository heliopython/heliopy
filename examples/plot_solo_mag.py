"""
Solar Orbiter MAG data
======================

Downloading and plotting MAG data from Solar Orbiter.
"""

###############################################################################
# Import the required modules
from datetime import datetime
import warnings

import astropy.units as u
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
import numpy as np

from heliopy.data.solo import download

###############################################################################
# Download some magnetic field data

data = download(datetime(2020, 6, 2), datetime(2020, 6, 3), 'MAG-RTN-NORMAL', 'L2')
print(data.columns)

###############################################################################
# Calculate the magnetic field mangitude
modB = np.sqrt(data.quantity('B_RTN_0')**2 +
               data.quantity('B_RTN_1')**2 +
               data.quantity('B_RTN_2')**2)
data = data.add_column('modB', modB)

###############################################################################
# Plot the data
fig, axs = plt.subplots(nrows=2, sharex=True)

ax = axs[0]
ax.plot(data.index, data.quantity('modB'))
ax.set_ylabel('nT')
ax.set_title(r'$|B|$')
ax.set_ylim(bottom=0)

ax = axs[1]
ax.plot(data.index, data.quantity('B_RTN_0'))
ax.set_ylabel('nT')
ax.set_title(r'$B_{r}$')
ax.axhline(0, color='black', linewidth=1, linestyle='--')

fig.suptitle('Solar Orbiter MAG L2 data')
ax.xaxis.set_major_formatter(
    mdates.ConciseDateFormatter(mdates.AutoDateLocator()))
plt.show()
