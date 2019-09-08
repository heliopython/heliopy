"""
Plotting OMNI Data
==================

Importing and plotting data from OMNI Web Interface.
OMNI provides interspersed data from various spacecrafts.
There are 55 variables provided in the OMNI Data Import.
"""

import heliopy.data.omni as omni
import matplotlib.pyplot as plt
from datetime import datetime

starttime = datetime(1970, 1, 1, 0, 0, 0)
endtime = datetime(1970, 1, 3, 0, 0, 0)

omni_data = omni.low(starttime, endtime)

fig, axs = plt.subplots(3, 1, sharex=True)
axs[0].plot(omni_data['Bx GSE, GSM'].data)
axs[1].plot(omni_data['By GSE'].data)
axs[1].plot(omni_data['Bz GSE'].data)
axs[2].plot(omni_data['By GSM'].data)
axs[2].plot(omni_data['Bz GSM'].data)

for ax in axs:
    ax.legend()
plt.show()
