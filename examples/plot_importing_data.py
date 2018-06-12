"""
Importing data
==============

A short example showing how to import and plot plasma data.
"""

from datetime import datetime, timedelta
import heliopy.data.helios as helios
import matplotlib.pyplot as plt

starttime = datetime(1976, 4, 5, 0, 0, 0)
endtime = starttime + timedelta(hours=12)
probe = '2'

corefit = helios.corefit(probe, starttime, endtime)

print(corefit.data.keys())

fig, axs = plt.subplots(3, 1, sharex=True)
axs[0].plot(corefit.data['n_p'])
axs[1].plot(corefit.data['vp_x'])
axs[1].plot(corefit.data['vp_y'])
axs[1].plot(corefit.data['vp_z'])
axs[2].plot(corefit.data['Tp_perp'])
axs[2].plot(corefit.data['Tp_par'])

for ax in axs:
    ax.legend()
plt.show()
