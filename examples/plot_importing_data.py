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

data = helios.corefit(probe, starttime, endtime)

print(data.keys())

fig, axs = plt.subplots(3, 1, sharex=True)
axs[0].plot(data['n_p'])
axs[1].plot(data['vp_x'])
axs[1].plot(data['vp_y'])
axs[1].plot(data['vp_z'])
axs[2].plot(data['Tp_perp'])
axs[2].plot(data['Tp_par'])

for ax in axs:
    ax.legend()
plt.show()
