What's new
==========

.. contents:: :local:
   :depth: 1

Version 0.3
-----------

New features
^^^^^^^^^^^^

Removed
^^^^^^^

- The `heliopy.plasma` module has been removed (see http://www.plasmapy.org/ for an alternative)
- `heliopy.plot.spectra` code removed

Version 0.2
-----------

New features
^^^^^^^^^^^^

- Convert examples gallery to automatically generate plots
- Added :meth:`HelioPy.data.helper.listdata` method for easily viewing the amount of data HelioPy is storing locally.
- Added :meth:`heliopy.data.wind.threedp_sfpd` method for importing WIND 3DP sfpd data.

Version 0.1.3
-------------

Fixed bugs
^^^^^^^^^^

- Correctly report download percentage when downloading files.
- Fix issue where :meth:`heliopy.data.helios.corefit` made duplicate .hdf files on days where no data is available.
