"""
Overview
--------
`SPICE`_ is a NASA toolkit for calculating the position of bodies
(including planets and spacecraft) within the solar system. This module builds
on the `spiceypy`_ package to provide a high level interface to the SPICE
toolkit for performing orbital calculations using spice kernels.

Integration with :mod:`astropy.coordinates`
-------------------------------------------
As well as allowing positions to be calculated in any coordinate system defined
in the `SPICE`_ toolkit, :mod:`heliopy.spice` can also construct
:class:`astropy.coordinates.SkyCoord` objects if the frame is implemented in
astropy or SunPy. See the documentaiton of
:meth:`heliopy.spice.Trajectory.coords()` for information on which frames are
supported.

.. _SPICE: https://naif.jpl.nasa.gov/naif/toolkit.html
.. _spiceypy: https://spiceypy.readthedocs.io/en/master/
"""
from .spice import *
from .data import get_kernel

import heliopy.spice.spice as _spice
import heliopy.spice.data as _data


for kernel in _data.generic_kernels:
    k = _data.get_kernel(kernel.short_name)
    _spice.furnish(k)
