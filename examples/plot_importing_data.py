"""
Importing data
==============

A short example showing how to import and plot plasma data.
"""

from datetime import datetime, timedelta
import heliopy.data.omni as omni
import matplotlib.pyplot as plt

starttime = datetime(2018, 12, 1)
endtime = starttime + timedelta(days=30)

tseries = omni.low(starttime, endtime)

print(tseries.data.keys())

fig, axs = plt.subplots(3, 1, sharex=True)
ax = axs[0]
ax.plot(tseries.index, tseries.quantity("Plasma Flow Speed"),
        label="$v_{sw}$")

ax = axs[1]
ax.plot(tseries.index, tseries.quantity("|B|"),
        label="$|B|$")

ax = axs[2]
ax.plot(tseries.index, tseries.quantity("Proton Density"),
        label="$n_p$")

for ax in axs:
    ax.legend()
plt.show()
