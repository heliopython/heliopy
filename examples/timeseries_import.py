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
endtime = datetime(1993, 1, 2, 0, 0, 0)

timeseries_data = ulysses.swics_abundances(starttime, endtime)

print(timeseries_data.data)  # Returns a Pandas DataFrame from the TimeSeries
print(timeseries_data.quantity('VEL_ALPHA'))  # Returns list-like data of the labeled column
print(timeseries_data.units)  # Returns the column names and the units attached

fig = timeseries_data.peek()  # Quick way to plot a TimeSeries function
