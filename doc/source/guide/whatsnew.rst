What's new
==========

.. contents:: :local:
   :depth: 2

Version 0.3
-----------

New features
^^^^^^^^^^^^

HelioPy now contiains code for working with SPICE kernels. See the following
modules for more information:

- :mod:`heliopy.data.spice` module for downloading spice kernels
- :mod:`heliopy.spice` module for automatically processing spice kernels

Removed features
^^^^^^^^^^^^^^^^

- The :mod:`heliopy.plasma` module has been removed
  (see http://www.plasmapy.org/ for the recommended alternative)
- :mod:`heliopy.plot` code removed

Version 0.2
-----------

New features
^^^^^^^^^^^^

- Convert examples gallery to automatically generate plots
- Added :meth:`HelioPy.data.helper.listdata` method for easily viewing the
  amount of data HelioPy is storing locally.
- Added :meth:`heliopy.data.wind.threedp_sfpd` method for importing
  WIND 3DP sfpd data.

Version 0.1.3
-------------

Fixed bugs
^^^^^^^^^^

- Correctly report download percentage when downloading files.
- Fix issue where :meth:`heliopy.data.helios.corefit` made duplicate .hdf
  files on days where no data is available.
