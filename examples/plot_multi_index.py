"""
A brief guide to pandas multi-index dataframes
==============================================

The data sets imported by heliopy are returned in a
:class:`pandas.DataFrame`. Most data sets have a
single variable for the :class:`DataFrame` index. In this case DataFrame can be
thought of as storing multiple variables, each of which depend on the same
dependent variable. For example the x component of magnetic field depends only
on time.

Particle distribution functions have more than one dependent variable however.
Typically the distribution is measured as a function of time, energy, and two
angles.
"""

import pandas as pd
import numpy as np

###############################################################################
# As a simple example, lets make a multi-index DataFrame to imitate a particle
# distribution function. First, set the index values

# Energy values
E = np.arange(0, 4)
# Azimuthal angles
phi = np.arange(0, 360, 90)
# Elevation angles
theta = np.arange(-90, 90, 45)
# Fake distribution function
dist = np.random.rand(E.size * phi.size * theta.size)

###############################################################################
# The index values can then be created from
# :meth:`pandas.MultiIndex.from_product`, and the complete DataFrame created
# from :meth:`pandas.DataFrame`. The distribution function is sorted first by
# energy, then by theta, and then by phi.

index = pd.MultiIndex.from_product((E, theta, phi),
                                   names=('E', 'theta', 'phi'))
data = pd.DataFrame(data=dist, index=index, columns=['df'])
print(data.head())

###############################################################################
# To loop through the energy levels with the index label ``'theta'`` do the
# following. ``theta`` will give the value of the current index, and
# ``theta_dist`` will give the reduced DataFrame at each value of ``theta``.

for theta, theta_data in data.groupby(level='theta'):
    print(theta)
