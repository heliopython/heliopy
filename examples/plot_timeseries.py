"""
TimeSeries Plotting Example
===========================

An example to show Sunpy's TimeSeries in HelioPy.

For more information on TimeSeries, see
http://docs.sunpy.org/en/stable/guide/data_types/timeseries.html

For more information on AstroPy Units, see
http://docs.astropy.org/en/stable/units/
"""

###############################################################################
# Import modules
import heliopy.data.ulysses as ulysses
import matplotlib.pyplot as plt
from datetime import datetime

###############################################################################
# Set up support for plotting data with units
from astropy.visualization import quantity_support
quantity_support()

###############################################################################
# Load data. In this example we use Ulysses data.
starttime = datetime(1993, 1, 1, 0, 0, 0)
endtime = datetime(1993, 2, 1, 0, 0, 0)
timeseries_data = ulysses.swics_abundances(starttime, endtime)

###############################################################################
# timeseries_data is a TimeSeries data type.
# The .index attribute gets the time index of the data
# the .quantity() method can be used to extract data with units attached

print(timeseries_data.data.keys())
fig, axs = plt.subplots(2, 1, sharex=True)
axs[0].plot(timeseries_data.index, timeseries_data.quantity('VEL_ALPHA'))

ion_ratios = ['RAT_C6_C5', 'RAT_O7_O6', 'RAT_FE_O']
for r in ion_ratios:
    axs[1].plot(timeseries_data.index, timeseries_data.quantity(r), label=r)

axs[1].set_yscale('log')
axs[1].legend()
plt.show()
