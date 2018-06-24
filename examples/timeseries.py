"""
TimeSeries Basics
=================

An example to show some basic functions of TimeSeries.

For more information about TimeSeries, http://docs.sunpy.org/en/stable/guide/data_types/timeseries.html
For more information about AstroPy Units, http://docs.astropy.org/en/stable/units/
"""

import numpy as np
import datetime
import pandas as pd
import sunpy.timeseries as ts
from collections import OrderedDict
import astropy.units as u

# The index of the SunPy Timeseries is always datetime
base = datetime.datetime.today()
times = [base - datetime.timedelta(minutes=x) for x in range(24*60, 0, -1)]
intensity = np.sin(np.arange(0, 12 * np.pi, ((12 * np.pi) / (24*60))))

# This example shows how a TimeSeries object is made from a Pandas DataFrame
data = pd.DataFrame(intensity, index=times, columns=['intensity'])

# TimeSeries can have a metadata attached to it.
meta = OrderedDict({'key':'value'})

# AstroPy Units are attached to the TimeSeries by passing it alongside the data.
# The units are stored in an OrderedDict object.
# Each key is the unit, and the value is the astropy representation of the same.
units = OrderedDict([('intensity', u.W/u.m**2)])
ts_custom = ts.TimeSeries(data, meta, units)

# Using sunpy.timeseries.TimeSeries.data will return a Pandas DataFrame of the TimeSeries object.
print(ts_custom.data)

# To view the units, sunpy.timeserise.TimeSeries.units can be used.
print(ts_custom.units)

# The values can be extracted along with their units as well.
#sunpy.timeseries.TimeSeries.quantity(column_name)[index]
print(ts_custom.quantity('intensity')[1])
