HelioPy 0.15.4 (2021-07-10)
===========================

Features
--------

- Added support for loading Voyager merged datasets in `heliopy.data.voyager.`. (`#992 <https://github.com/heliopython/heliopy/pull/992>`__)


Bug Fixes
---------

- Fixed downloading PSP/FIELDS data. (`#988 <https://github.com/heliopython/heliopy/pull/988>`__)
- Updated the PSP SPICE kernels to their latest versions. (`#989 <https://github.com/heliopython/heliopy/pull/989>`__)


HelioPy 0.15.3 (2021-03-29)
===========================

Features
--------

- Level 3 data products can now be downloaded using `heliopy.data.solo.download`. (`#966 <https://github.com/heliopython/heliopy/pull/966>`__)


Bug Fixes
---------

- Fixed access to some Solar Orbiter SWA data products in `heliopy.data.solo`. (`#957 <https://github.com/heliopython/heliopy/pull/957>`__)


Trivial/Internal Changes
------------------------

- Updated links to PSP SPICE kernels in `heliopy.data.spice`. (`#961 <https://github.com/heliopython/heliopy/pull/961>`__)
- Improved performance of `heliopy.spice.Trajectory.generate_positions`. (`#963 <https://github.com/heliopython/heliopy/pull/963>`__)


HelioPy 0.15.2 (2020-12-23)
===========================
Bug fixes
---------
- Fixed a bug in :file:`setup.py` that prevented HelioPy from being installed
  on other readthedocs projects.

Heliopy 0.15.0 (2020-10-17)
===========================

Features
--------

- All SPICE kernels are now automatically furnished when they are loaded into
  a `~heliopy.spice` object. (`#938 <https://github.com/heliopython/heliopy/pull/938>`__)
- The classes in `heliopy.data.spice` have been updated, to allow for different
  types of SPICE files:

  - All kernels are now derived from `KernelBase`.
  - SPK kernels have their own class, `SPKKernel`.
  - Calling `Kernel` will automatically detect and create the appropriate kernel
    class. (`#941 <https://github.com/heliopython/heliopy/pull/941>`__)


Bug Fixes
---------

- When a `SPKKernel` is created, the SPICE kernel is now validated and an error
  raised if the given file is not a valid SPK kernel. (`#941 <https://github.com/heliopython/heliopy/pull/941>`__)
- Updated link to the Solar Orbiter SPICE kernel (`#942 <https://github.com/heliopython/heliopy/pull/942>`__)


Heliopy 0.14.0 (2020-09-30)
===========================

Features
--------

- Added the ability to download science quality data to `heliopy.data.solo.download`. (`#934 <https://github.com/heliopython/heliopy/pull/934>`__)


Bug Fixes
---------

- SWEAP functions in `heliopy.data.psp` have been updated to take into account
  a change in file version number that occurred at the end of 2019. (`#932 <https://github.com/heliopython/heliopy/pull/932>`__)


Heliopy 0.13.1 (2020-08-27)
===========================

Features
--------

- Added `~heliopy.data.stereo.mag_l1_rtn` and `~heliopy.data.stereo.magplasma_l2`
  to `heliopy.data.stereo`. (`#928 <https://github.com/heliopython/heliopy/pull/928>`__)
- `heliopy.data.stereo` functions now also accept ``'STA'`` or ``'STB'`` as a
  spacecraft identifier. (`#929 <https://github.com/heliopython/heliopy/pull/929>`__)


Bug Fixes
---------

- Fixed the download URL for functions in `heliopy.data.helios`. (`#927 <https://github.com/heliopython/heliopy/pull/927>`__)


Heliopy 0.13.0 (2020-08-21)
===========================

Features
--------

- Added `heliopy.data.psp.merged_mag_plasma` for merged plasma and magnetic field
  data from PSP. (`#912 <https://github.com/heliopython/heliopy/pull/912>`__)
- Added the ability to download Solar Orbiter low latency data in
  `heliopy.data.solo.download`. (`#919 <https://github.com/heliopython/heliopy/pull/919>`__)
- Added the `heliopy.data.stereo` module, with `~heliopy.data.stereo.coho1hr_merged`.
  To request more STEREO data products, please open an issue at
  https://github.com/heliopython/heliopy/issues. (`#923 <https://github.com/heliopython/heliopy/pull/923>`__)


Backwards Incompatible Changes
------------------------------

- Support for converting from the ``J2000`` coordinate frame to astropy
  coordinates has been removed in `heliopy.spice.Trajectory.coords`. If you want
  to convert to astropy coordinates, generate the trajectory in the ``IAU_SUN``
  coordinate system, get the coords, and then ``.transform_to()`` the desired
  astropy coordinate frame from there. (`#913 <https://github.com/heliopython/heliopy/pull/913>`__)


Bug Fixes
---------

- The coordinates returned by `heliopy.spice.Trajectory.coords` when the
  coordinate frame is ``"IAU_SUN"`` have been fixed to properly take into account
  light travel time. In order to ensure consistency, coordinates can only be
  created with sunpy versions > 2. (`#911 <https://github.com/heliopython/heliopy/pull/911>`__)


Heliopy 0.12.0 (2020-06-22)
===========================

Features
--------

- Added `heliopy.data.psp.fields_mag_rtn_4_per_cycle` download function. (`#896 <https://github.com/heliopython/heliopy/pull/896>`__)
- Added 1 minute and 5 minute OMNI data products to `heliopy.data.omni`. (`#907 <https://github.com/heliopython/heliopy/pull/907>`__)
- Added ``'mec'`` to the list of allowed instruments in `heliopy.data.mms`. (`#908 <https://github.com/heliopython/heliopy/pull/908>`__)


Backwards Incompatible Changes
------------------------------

- The OMNI data download functions have been updated to use CDAWeb as their source.
  This means that the ``heliopy.data.omni.low`` function has been removed, and
  replaced by `heliopy.data.omni.h0_mrg1hr`. This is the same 1 hour data product,
  but some of the variable names will have changed. (`#904 <https://github.com/heliopython/heliopy/pull/904>`__)


Heliopy 0.11.1 (2020-05-19)
===========================

Features
--------

- Added `heliopy.data.psp.fields_mag_rtn_4_per_cycle`. (`#896 <https://github.com/heliopython/heliopy/pull/896>`__)


Bug Fixes
---------

- Fixed Solar Orbiter kernel download in `heliopy.data.spice`. (`#898 <https://github.com/heliopython/heliopy/pull/898>`__)
- ``heliopy.spice.setup_spice`` no longer needs to be manually run to setup common spice files. (`#899 <https://github.com/heliopython/heliopy/pull/899>`__)


Improved Documentation
----------------------

- Fixed the documentation build on readthedocs. (`#894 <https://github.com/heliopython/heliopy/pull/894>`__)


Heliopy 0.11.0 (2020-05-11)
===========================

Changes to `heliopy.spice`
--------------------------

This release contains several breaking changes to `heliopy.spice` and
`heliopy.data.spice`, made to accommodate new high level objects to interact
with SPICE. The following new objects have been added:

- `~heliopy.spice.SPKKernel`, to hold a single SPICE SPK kernel. This comes
  with helper methods to find the bodies stored within a kernel, and the time
  coverage of a given body within a kernel.
- `~heliopy.spice.Body`, to hold a single body (e.g. a planet, a spacecraft).
  This contains helper methods to easily convert between body names and body
  ids.

In addition, `heliopy.spice` no longer automatically loads commonly needed
files on import. This means if you want to use `heliopy.spice`, it is highly
recommended to run `heliopy.spice.setup_spice()` first.

The existing code has been changed to use the new classes, with the following
breaking changes:

- `heliopy.data.spice.get_kernel` now returns a list of `~heliopy.spice.SPKKernel`.
  To get the file name of a kernel as before do ``kernel.fname``.
- `heliopy.spice.furnish` must how take a `~heliopy.spice.SPKKernel` (or list of).
  To create a kernel object from a filename do ``SPKKernel(fname)``.

Features
--------

- :mod:`heliopy.spice` now contains the :class:`~heliopy.spice.Body` object, which
  allows for easy access of both a body name and id code, validating that either a name
  or id code are valid on creation.

- :class:`~heliopy.spice.Trajctory` now stores the ``.target`` and ``.observing``
  body atributes as :class:`~heliopy.spice.Body` objects. To get the name or id,
  use ``.id`` or ``.name``. (`#868 <https://github.com/heliopython/heliopy/pull/868>`__)
- Added the ``abcorr`` argument to `heliopy.spice.Trajectory.generate_positions()`
  to allow optional aberration correction. By default this is set to no correction. (`#873 <https://github.com/heliopython/heliopy/pull/873>`__)
- Added the Cassini SPICE kernel to `heliopy.data.spice`. (`#876 <https://github.com/heliopython/heliopy/pull/876>`__)
- Updated the Solar Orbiter SPICE kernel to the latest release in `heliopy.data.spice`. (`#879 <https://github.com/heliopython/heliopy/pull/879>`__)
- Added several new solar energetic particle products to `heliopy.data.ace`. (`#882 <https://github.com/heliopython/heliopy/pull/882>`__)


Heliopy 0.10.1 (2020-04-03)
===========================

Bug Fixes
---------

- Updated the url for downloading Helios 4Hz magnetic field data. (`#856 <https://github.com/heliopython/heliopy/pull/856>`__)
- Avoid converting all CDF data to floating point data, to save significant memory when loading a CDF file. (`#858 <https://github.com/heliopython/heliopy/pull/858>`__)


Heliopy 0.10.0 (2020-02-20)
===========================

Features
--------

- Added PSP SWEAP level 2 data to `heliopy.data.psp`. (`#828 <https://github.com/heliopython/heliopy/pull/828>`__)
- Added PSP FIELDS high resolution data import to `heliopy.data.psp`. (`#842 <https://github.com/heliopython/heliopy/pull/842>`__)
- `heliopy.spice.Trajectory.generate_positions` now accepts times as anything that
  can be parsed by `astropy.time.Time`. (`#831 <https://github.com/heliopython/heliopy/pull/831>`__)
- Added a ``include`` argument to `heliopy.data.util.cdf2df`, to allow
  loading a subset of variables in a CDF file. (`#841 <https://github.com/heliopython/heliopy/pull/841>`__)
- Improved time performance of loading CDF files. (`#844 <https://github.com/heliopython/heliopy/pull/844>`__, `#845 <https://github.com/heliopython/heliopy/pull/845>`__, `#847 <https://github.com/heliopython/heliopy/pull/847>`__)
- Bad values in CDF files are now automatically detected and set to NaN values.
  As a result the ``badvalues`` argument to `heliopy.data.util.cdf2df` is
  now deprecated. (`#848 <https://github.com/heliopython/heliopy/pull/848>`__)


Improved Documentation
----------------------

- Cleaned up the docstrings of `heliopy.data`. (`#846 <https://github.com/heliopython/heliopy/pull/846>`__)


Heliopy 0.9.0 (2019-11-13)
==========================

Features
--------

- A new module `heliopy.models` has been added to contain
  heliospheric concepts, the first one of which is
  :class:`heliopy.models.ParkerSpiral`. (`#768 <https://github.com/heliopython/heliopy/pull/768>`__)
- All functions in `heliopy.data.wind` now download data in monthly
  (as opposed to daily) intervals. You may need to delete existing data to
  correctly load complete datasets. (`#772 <https://github.com/heliopython/heliopy/pull/772>`__)
- :class:`heliopy.spice.Trajectory` objects now have the
  :attr:`~heliopy.spice.Trajectory.coords` property, that contains the trajectory
  coordinates as an :class:`~astropy.coordinates.SkyCoord` object.

  In order to do this
  currently only the 'J2000' and 'IAU_SUN' spice frames are supported as they
  have direct mappings to Sunpy/Astropy coordinate systems, but it is possible
  to generate coordinates in either of these systems and then transform them
  post-hoc to another Sunpy/Astropy coordinate system. (`#776 <https://github.com/heliopython/heliopy/pull/776>`__)
- `heliopy.data.wind.swe_h3()` has been added. (`#800 <https://github.com/heliopython/heliopy/pull/800>`__)
- `heliopy.data.wind.threedp_elpd()` has been added. (`#802 <https://github.com/heliopython/heliopy/pull/802>`__)
- The new `heliopy.data.psp` module contains methods to automatically download
  and load Parker Solar Probe data. Currently SWEAP SPC L3 data and FIELDS MAG
  fluxgate data are available. (`#822 <https://github.com/heliopython/heliopy/pull/822>`__)


Backwards Incompatible Changes
------------------------------

- A handful of data download functions have migrated to using the CDAS restful
  service, and have therefore had their call signatures changed. In particular
  the following functions have lost their ``try_download`` keyword argument:
  `heliopy.data.ulysses.swics_heavy_ions` (`#747 <https://github.com/heliopython/heliopy/pull/747>`__),
  `heliopy.data.ulysses.swics_abundances` (`#747 <https://github.com/heliopython/heliopy/pull/747>`__),
  `heliopy.data.ulysses.fgm_hires` (`#748 <https://github.com/heliopython/heliopy/pull/748>`__),
  `heliopy.data.ulysses.swoops_ions` (`#761 <https://github.com/heliopython/heliopy/pull/761>`__),
  `heliopy.data.omni.low` (`#765 <https://github.com/heliopython/heliopy/pull/765>`__),
  `heliopy.data.imp.merged` (`#771 <https://github.com/heliopython/heliopy/pull/771>`__)
- The times stored in the ``time`` property of :class:`heliopy.spice.Trajectory`
  are now always parsed by `astropy.time.Time` before being stored, and are
  always returned as a `~astropy.time.Time` object, no matter what format they
  were supplied in. (`#794 <https://github.com/heliopython/heliopy/pull/794>`__)
- The ``heliopy.coordinates`` module has been removed completely. This only ever
  contained two coordinate frames and a single transformation, both of which are
  implemented in `sunpy.coordinates` now. (`#820 <https://github.com/heliopython/heliopy/pull/820>`__)
- `heliopy.data.cassini` data download methods have been updated to use the newly released V2
  Cassini MAG data. You may need to delete old data to be able to download the
  newer data.


Bug Fixes
---------

- Fixed a bug in loading .cdf data where either all files were either converted
  to .hdf files or at least one of the intervals of data is missing. (`#768 <https://github.com/heliopython/heliopy/pull/768>`__)
- Fixed downloading narrow time intervals of MMS data. (`#810 <https://github.com/heliopython/heliopy/pull/810>`__)


Heliopy 0.8.2 (2019-10-21)
==========================

Features
--------

- Added the SOHO SPICE kernels to `heliopy.data.spice`. (`#777 <https://github.com/heliopython/heliopy/pull/777>`__)


Bug Fixes
---------

- `heliopy.data.spice` can now be imported without internet access. If this
  is the case determining the names of STEREO kernels (which requires internet)
  will not be possible. (`#782 <https://github.com/heliopython/heliopy/pull/782>`__)
- Fixed loading Ulysses data when at least some of it isn't available. (`#795 <https://github.com/heliopython/heliopy/pull/795>`__)


HelioPy 0.8.1 (2019-08-14)
==========================

Bug Fixes
---------

- Fix `heliopy.data.helios.mag_4hz` data downloading (`#741 <https://github.com/heliopython/heliopy/pull/741>`__)
- Switch IMP downloading from FTP site to HTTPS site, since anonymous FTP access
  to NASA servers no longer works. (`#749 <https://github.com/heliopython/heliopy/pull/749>`__)


HelioPy 0.8.0 (2019-06-24)
==========================

Features
--------

- `heliopy.data.cdasrest.get_cdas_url` and `heliopy.data.cdasrest.get_data`
  have been generalised, and can now be used to download data in an arbitrary
  interval instead of just a single day. (`#714 <https://github.com/heliopython/heliopy/pull/714>`__)
- `heliopy.data.ace` functions that download low cadence data (e.g. composition
  data) now download yearly instead of daily files, speeding up data download. (`#715 <https://github.com/heliopython/heliopy/pull/715>`__)


Backwards Incompatible Changes
------------------------------

- `heliopy.data.cdasrest.get_cdas_url` and `heliopy.data.cdasrest.get_data`
  now take ``starttime`` and ``endtime`` arguments instead of just a ``date``
  argument, and their signatures have changed to reflect this. (`#714 <https://github.com/heliopython/heliopy/pull/714>`__)


HelioPy 0.7.1 (2019-06-10)
==========================

Bug Fixes
---------

- Fix bug that prevented MMS data from spacecraft 4 being downloaded. (`#719 <https://github.com/heliopython/heliopy/pull/719>`__)
- Correctly attach units to MMS data. (`#726 <https://github.com/heliopython/heliopy/pull/726>`__)

Version 0.7.0
=============

New features
------------

- Added a graph showing the available coordinate transformations to
  ``heliopy.coordinates``
- Added STEREO-B kernels to `heliopy.data.spice`
- Added automatic spice kernel detection for the STEREO spacecraft to
  `heliopy.data.spice`
- Switched the download progress bar from ``wget`` based to ``tqdm`` based,
  which should work better in notebooks.

Bug fixes
---------

- Fixed a bug where not all MMS files were downloaded for a large query.
- Correctly removed bad values in `heliopy.data.omni`.

Removed features
----------------

- The deprecated `heliopy.data.wind.swe_h3` and
  `heliopy.data.wind.threedp_sfpd` have been removed.


Version 0.6.7
=============

Deprecations
------------

- `heliopy.data.wind.swe_h3` and `heliopy.data.wind.threedp_sfpd`
  are deprecated and will be removed in version 0.7.0. This is because they
  currently use pandas MultiIndex structures, which are not the recommended
  way to store 2-or-more dimensional data. In the future they are likely to be
  re-written to use xarray.

Version 0.6.6
=============

Bug fixes
---------

- Data downloaded through CDAS is now moved from a temporary folder using
  ``shutil``, fixing it when the temp folder and destination folder are on
  different filesystems.

Version 0.6.5
=============

Bug fixes
---------

- `heliopy.data.spice.get_kernel` now raises a warning instead of an
  error if a kernel can't be downloaded.
- `heliopy.data.helios.merged` now filters out bad values and converts
  them to NaNs.
- `heliopy.spice` now only loads core SPICE kernels once, instead of every
  time the module is imported.

Backwards incompatible changes
------------------------------

- `heliopy.data.spice.get_kernel` now prints a warning instead of
  raising an error if a kernel cannot be downloaded.

Version 0.6.4
=============

New features
------------

- Added the ability for :class:`heliopy.spice.Trajectory` objects to compute
  and return the body velocity.
- Available spice kernels in `heliopy.data.spice` are now split into
  kernels that have been reconstructed (ie. actual trajectories) and
  predicted trajectories.
- The predicted Bepi Columbo spice kernel has been added to
  `heliopy.data.spice`
- The `heliopy.data.ace.swi_h3b` function has been added.
- `heliopy.data.cdasrest.get_variables` and
  `heliopy.data.cdasrest.get_data` now have a ``timeout`` keyword
  argument, allowing manual specification of the timeout when fetching data
  from a server.
- Importing `heliopy.spice` now automatically loads common heliospheric
  coordinate systems.

Backwards incompatible changes
------------------------------

- Kernels available in `heliopy.data.spice` have been cleaned up,
  meaning some are now not available or have been moved to the predicted
  section.
- A handful of data download functions have migrated to using the CDAS restful
  service, and have therefore had their call signatures changed. In particular:
  - `heliopy.data.messenger.mag_rtn` has lost its ``try_download`` kwarg
  - `heliopy.data.helios.merged` has lost its ``try_download`` kwarg

The following IMP download functions, which only ever worked for IMP8 have
been renamed:

- ``mitplasma_h0`` has been renamed `~heliopy.data.imp.i8_mitplasma`
- ``mag320ms`` has been renamed `~heliopy.data.imp.i8_mag320ms`

Version 0.6.3
=============

New features
------------

- Added Parker Solar Probe spice kernels to `heliopy.data.spice`.
- Added a generic functions to download MMS data. Available files can be
  queried using `heliopy.data.mms.available_files`, and files can be
  downloaded using `heliopy.data.mms.download_files`

Bug fixes
---------

- Updated links to the STEREO-A spice kernels.

Backwards incompatible changes
------------------------------

- `heliopy.data.mms.fgm_survey` has been removed in favour of the more
  general `heliopy.data.mms.fgm`. To download survey mode FGM data use
  the new method and set the ``mode`` keyword argument to ``srvy``.

Version 0.6.2
=============

New features
------------

- Added `heliopy.data.mms.fpi_des_moms` function. :issue:`601`
- Added `heliopy.data.wind.threedp_e0_emfits` function. :issue:`606`

Bug fixes
---------

- Fixed `heliopy.data.mms.fgm_survey` data loading. :issue:`601`

Version 0.6.1
=============

New features
------------
- The `heliopy.data.ace` module now contains all the magnetic field and
  particle data produces produced by ACE. :issue:`577`, :issue:`578`
- STEREO-A spice kernels have been added. :issue:`585`


Bug fixes
---------
- The accidentally removed Ulysses spice kernel has returned. :issue:`582`
- `heliopy.data.helper.cdfpeek` has been updated to work with cdflib, and now
  prints all CDF file information.

Version 0.6.0
=============

HelioPy now only supports Python versions 3.6 and higher.

New features
------------
- HelioPy has been integrated with SunPy TimeSeries and AstroPy Units. All of
  the HelioPy modules now return physical units with data.
- Added a new `.data.util.cdf_units` function that can extract the UNIT
  attribute from CDF files.
- Low resolution OMNI data import has been added in
  `.data.omni.low` function.
- Magnetic Field data from DSCOVR Spacecraft
  can now be imported using the `.data.dscovr.mag_h0` function.

Backwards incompatible changes
------------------------------
- Methods in `heliopy.data` no longer returns a Pandas DataFrame, but
  now return a SunPy timeseries object. To get the underlying data, you can
  still do::

    dataframe = timeseries.data

  For an example of how to use the new object, see
  :ref:`sphx_glr_auto_examples_timeseries_plotting.py`.
- Data import has had a major overhaul, so that every column in CDF files now
  gets automatically imported and retains its name without being changed by
  HelioPy. This means column names in several data products are now different,
  to reflect their original name in the CDF files instead of a custom name
  that was previously assigned by HelioPy.
- `.data.helios.merged`, `.data.helios.mag_4hz`,
  `.data.helios.corefit` and `.data.helios.mag_ness` no longer take
  a ``verbose`` keyword argument. :issue:`467`


Fixed bugs
----------
- `.data.imp.merged` no longer imports redundant columns.

Version 0.5.3
=============

New features
------------

- Lots of small documentation updates.
- `.data.helios.distparams` now has an extra ``'data_rate'`` column, which
  determines whether a given distribution function was transmitted in high or
  low data mode. :issue:`529`

Version 0.5.2
=============

New features
------------

- The new HelioPy logo has been added to the documentation.
  :issue:`448`, :issue:`447`

Fixed bugs
----------

- The new data version number of `heliopy.data.mms.fpi_dis_moms` has been
  updated.


Version 0.5.1
=============

New features
------------

- HelioPy can now be installed using conda.

Backwards incompatible changes
------------------------------
- The list of kernels available for automatic download in `heliopy.data.spice`
  has been updated, and some names changed. :issue:`408`

Fixed bugs
----------
- `.spice.Trajectory.generate_positions` can now generate
  positions at a resolution of one second instead of one day. :issue:`405`
- A duplicate "z gsm" column header in the data returned by
  `.data.imp.mag15s` has been corrected. :issue:`396`

Version 0.5.0
=============

New features
------------

- `heliopy.data.sunspot` added an additional functionality to import
  sunspot data in three different timeframes - daily, monthly and yearly.
- The inventory of spice kernels in `heliopy.data.spice` now includes
  "Helios 1 Reconstructed", "Helios 1 Predicted", "Juno Reconstructed",
  "Juno Predicted" and "Helios 2" kernels.
- `heliopy.spice.furnish` now accepts a list of filenames as well as
  individual filenames.
- A lot of new functions for downloading ACE data have been added to
  `heliopy.data.ace`.

Backwards incompatible changes
------------------------------

- `heliopy.data.spice.get_kernel` now returns a list of filenames instead
  of a single filename string.
- Most of the functions that were in `heliopy.data.helper` have been
  moved to `heliopy.data.util`. The ones the remain in
  `heliopy.data.helper` are useful for users, and the ones in
  `heliopy.data.util` are used internally as utility functions for
  data import.

Removed features
----------------

- ``heliopy.data.helios.trajectory`` has been removed. To get Helios
  trajectory data use the `heliopy.spice` and `heliopy.data.spice`
  modules.

Version 0.4
===========

New features
------------

- `~heliopy.data.ulysses.swics_abundances` and
  `~heliopy.data.ulysses.swics_heavy_ions`
  methods added for loading SWICS data from the Ulysses mission.
- `~heliopy.data.helper.cdfpeek` method added for peeking inside
  CDF files.

Backwards incompatible changes
------------------------------

- `heliopy.spice.Trajectory.generate_positions` now takes a list of
  dates/times at which to generate orbital positions, instead of a start time,
  stop time, and number of steps. The old behaviour can be recovered by
  manually generating an evenly spaced list of times.

Version 0.3
===========

New features
------------

HelioPy now contiains code for working with SPICE kernels. See the following
modules for more information:

- `heliopy.data.spice` module for downloading spice kernels
- `heliopy.spice` module for automatically processing spice kernels

Removed features
----------------

- The ``heliopy.plasma`` module has been removed
  (see http://www.plasmapy.org/ for the recommended alternative)
- ``heliopy.plot`` code removed

Version 0.2
===========

New features
------------

- Convert examples gallery to automatically generate plots
- Added `heliopy.data.helper.listdata` method for easily viewing the
  amount of data HelioPy is storing locally.
- Added `heliopy.data.wind.threedp_sfpd` method for importing
  WIND 3DP sfpd data.

Version 0.1.3
=============

Fixed bugs
----------

- Correctly report download percentage when downloading files.
- Fix issue where `heliopy.data.helios.corefit` made duplicate .hdf
  files on days where no data is available.
