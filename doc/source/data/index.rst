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
-----------------------------

HelioPy is built to be used alongside SunPy and AstroPy. Before V0.6, HelioPy returned
a Pandas DataFrame object. After implementation of physical units, HelioPy now
returns a SunPy TimeSeries object. The TimeSeries object is capable of storing units data,
and works well with AstroPy.

SunPy TimeSeries Documentation is available
at http://docs.sunpy.org/en/v0.9.0/guide/data_types/timeseries.html

AstroPy Units Documentation is available
at http://docs.astropy.org/en/stable/units/
