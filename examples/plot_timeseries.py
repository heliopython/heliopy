"""
TimeSeries Example
==================

An example to show some basic, but very important functions in Sunpy's TimeSeries.

For more information about TimeSeries, http://docs.sunpy.org/en/stable/guide/data_types/timeseries.html
For more information about AstroPy Units, http://docs.astropy.org/en/stable/units/
"""

import heliopy.data.ulysses as ulysses
import matplotlib.pyplot as plt
from datetime import datetime

starttime = datetime(1993, 1, 1, 0, 0, 0)
endtime = datetime(1993, 2, 1, 0, 0, 0)

timeseries_data = ulysses.swics_abundances(starttime, endtime)

# timeseries_data is a TimeSeries data type
# Using the timeseries.data function, one can obtain the Pandas DataFrame of the data

print(timeseres_data.data.keys())
fig, axs = plt.subplots(2, 1, sharex=True)
axs[0].plot(timeseries_data.data['VEL_ALPHA'])
axs[1].plot(timeseries_data.data['RAT_C6_C5'])
axs[1].plot(timeseries_data.data['RAT_O7_O6'])
axs[1].plot(timeseries_data.data['RAT_FE_O'])

for ax in axs:
    ax.legend()
plt.show()
