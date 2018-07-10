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
util module:

.. toctree::
   :maxdepth: 1

   util
