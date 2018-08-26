Version 0.6.0
-------------

HelioPy now only supports Python versions 3.6 and higher.

New features
^^^^^^^^^^^^
- HelioPy has been integrated with SunPy TimeSeries and AstroPy Units. All of
  the HelioPy modules now return physical units with data.
- Added a new :func:`.data.util.cdf_units` function that can extract the UNIT
  attribute from CDF files.
- Low resolution OMNI data import has been added in
  :func:`.data.omni.low` function.
- Magnetic Field data from DSCOVR Spacecraft
  can now be imported using the :func:`.data.dscovr.mag_h0` function.

Backwards incompatible changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- Methods in :mod:`heliopy.data` no longer returns a Pandas DataFrame, but
  now return a SunPy timeseries object. To get the underlying data, you can
  still do::

    dataframe = timeseries.data

  For an example of how to use the new object, see
  :ref:`sphx_glr_auto_examples_plot_timeseries.py`.
- Data import has had a major overhaul, so that every column in CDF files now
  gets automatically imported and retains its name without being changed by
  HelioPy. This means column names in several data products are now different,
  to reflect their original name in the CDF files instead of a custom name
  that was previously assigned by HelioPy.
- :func:`.data.helios.merged`, :func:`.data.helios.mag_4hz`,
  :func:`.data.helios.corefit` and :func:`.data.helios.mag_ness` no longer take
  a `verbose` keyword argument. :issue:`467`


Fixed bugs
^^^^^^^^^^
- :func:`.data.imp.merged` no longer imports redundant columns.

Version 0.5.3
-------------

New features
^^^^^^^^^^^^

- Lots of small documentation updates.
- `.data.helios.distparams` now has an extra ``'data_rate'`` column, which
  determines whether a given distribution function was transmitted in high or
  low data mode. :issue:`529`

Version 0.5.2
-------------

New features
^^^^^^^^^^^^

- The new HelioPy logo has been added to the documentation.
  :issue:`448`, :issue:`447`

Fixed bugs
^^^^^^^^^^

- The new data version number of :meth:`.data.mms.fpi_dis_moms` has been
  updated.


Version 0.5.1
-------------

New features
^^^^^^^^^^^^

- HelioPy can now be installed using conda.

Backwards incompatible changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- The list of kernels available for automatic download in :mod:`.data.spice`
  has been updated, and some names changed. :issue:`408`

Fixed bugs
^^^^^^^^^^
- :meth:`.spice.Trajectory.generate_positions` can now generate
  positions at a resolution of one second instead of one day. :issue:`405`
- A duplicate "z gsm" column header in the data returned by
  :meth:`.data.imp.mag15s` has been corrected. :issue:`396`

Version 0.5.0
-------------

New features
^^^^^^^^^^^^

- :meth:`heliopy.data.sunspot` added an additional functionality to import
  sunspot data in three different timeframes - daily, monthly and yearly.
- The inventory of spice kernels in :mod:`heliopy.data.spice` now includes
  "Helios 1 Reconstructed", "Helios 1 Predicted", "Juno Reconstructed",
  "Juno Predicted" and "Helios 2" kernels.
- :meth:`heliopy.spice.furnish` now accepts a list of filenames as well as
  individual filenames.
- A lot of new functions for downloading ACE data have been added to
  :mod:`heliopy.data.ace`.

Backwards incompatible changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- :meth:`heliopy.data.spice.get_kernel` now returns a list of filenames instead
  of a single filename string.
- Most of the functions that were in :mod:`heliopy.data.helper` have been
  moved to :mod:`heliopy.data.util`. The ones the remain in
  :mod:`heliopy.data.helper` are useful for users, and the ones in
  :mod:`heliopy.data.util` are used internally as utility functions for
  data import.

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
