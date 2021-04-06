"""
Solar Orbiter low latency data
==============================

Downloading and plotting low latency data from Solar Orbiter.
Note that this data is not suitable for publication.
"""

###############################################################################
# Import the required modules
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import dates as mdates

from heliopy.data.solo import download

###############################################################################
# Download some magnetic field data

data = download(datetime(2020, 7, 10), datetime(2020, 8, 3), 'MAG', 'LL02')
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

fig.suptitle('Solar Orbiter MAG low latency (not for science use)')
ax.xaxis.set_major_formatter(
    mdates.ConciseDateFormatter(mdates.AutoDateLocator()))
plt.show()
