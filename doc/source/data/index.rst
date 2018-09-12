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
   dscovr
   helios
   imp
   messenger
   mms
   omni
   ulysses
   wind

Each mission does not have a complete set of data import methods, but the goal
of HelioPy is to be as complete as possible. If you want to import a data set
that is not yet supported please open an issue on the bug tracker at
https://github.com/heliopython/heliopy/issues

There are also modules for downloading SPICE kernels and sunspot number
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
cdas and util modules:

.. toctree::
   :maxdepth: 1

   cdas
   util

SunPy and AstroPy Integration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

HelioPy is built to be used alongside SunPy and astropy. Before v0.6, HelioPy
returned a pandas DataFrame object. After adding physical units to the data,
HelioPy now returns a SunPy TimeSeries object.
The TimeSeries object is capable of storing the data in a DataFrame, and also
stores the units that are associated with each data column.

An example on how to use TimeSeries data and astropy units is also available
in :ref:`sphx_glr_auto_examples_plot_timeseries.py`.
