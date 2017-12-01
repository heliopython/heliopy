What's new
==========

.. contents:: :local:
   :depth: 1


version 0.2
-----------

New features
^^^^^^^^^^^^

- Added :meth:`heliopy.data.helper.listdata` method for easily viewing the amount of data heliopy is storing locally
- Added :meth:`heliopy.data.wind.threedp_sfpd` method for importing WIND 3DP sfpd data

Version 0.1.3
-------------

Fixed bugs
^^^^^^^^^^

- Correctly report download percentage when downloading files
- Fix issue where :meth:`heliopy.data.helios.corefit` made duplicate .hdf files on days where no data is available
