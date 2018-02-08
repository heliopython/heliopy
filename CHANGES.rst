Version 0.5
-----------

New features
^^^^^^^^^^^^

- The inventory of spice kernels in :mod:`heliopy.data.spice` now includes
  "Helios 1" and "Helios 2".
- :meth:`heliopy.spice.furnish` now accepts a list of filenames as well as
  individual filenames.

Backwards incompatible changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- :meth:`heliopy.data.spice.get_kernel` now returns a list of filenames instead
  of a single filename string.

Removed features
^^^^^^^^^^^^^^^^

- :meth:`heliopy.data.helios.trajectory` has been removed. To get Helios
  trajectory data use the :mod:`heliopy.spice` and :mod:`heliopy.data.spice`
  modules.

Version 0.4
-----------

New features
^^^^^^^^^^^^

- :meth:`~heliopy.data.ulysses.swics_abundances` and
  :meth:`~heliopy.data.ulysses.swics_heavy_ions`
  methods added for loading SWICS data from the Ulysses mission.
- :meth:`~heliopy.data.helper.cdfpeek` method added for peeking inside
  CDF files.
- :meth:`~heliopy.data.ace.swi_h2` data import method added for ACE SWICS data.

Backwards incompatible changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- :meth:`heliopy.spice.Trajectory.generate_positions` now takes a list of
  dates/times at which to generate orbital positions, instead of a start time,
  stop time, and number of steps. The old behaviour can be recovered by
  manually generating an evenly spaced list of times.

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
