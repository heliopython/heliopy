.. _heliopy-data:

Data import (:mod:`heliopy.data`)
---------------------------------

.. currentmodule:: heliopy.data

Methods for automatically importing data to python. Each spacecraft has its
own sub-module:

.. toctree::
   :maxdepth: 1

   ace
   artemis
   cassini
   cluster
   helios
   imp
   messenger
   mms
   ulysses
   wind

There is also other modules for downloading SPICE kernels and sunspot number
data:

.. toctree::
   :maxdepth: 1

   spice
   sunspot

a module with helper functions that apply generally to all data is available:

.. toctree::
   :maxdepth: 1

   helper

and utility functions that much of the data import uses are also available in the
util module:

.. toctree::
   :maxdepth: 1

   util

SunPy and AstroPy Integration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

HelioPy is built to be used alongside SunPy and AstroPy. Before v0.6, HelioPy returned
a Pandas DataFrame object. After implementation of physical units into the data, HelioPy
returns a SunPy TimeSeries object. The TimeSeries object is capable of storing data like Pandas DataFrame,
with added benefit of being used alongside AstroPy units.

SunPy Documentation is available at http://docs.sunpy.org/
You can also read more about ..TimeSeries: docs.sunpy.org/en/stable/guide/data_types/timeseries.html

AstroPy Documentation is available at http://docs.astropy.org/
You can also read mroe about ..Units: http://docs.astropy.org/en/stable/units/
