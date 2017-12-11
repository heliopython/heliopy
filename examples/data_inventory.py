'''
Local data inventory
====================

:mod:`heliopy.data.helper` contains the method
:meth:`heliopy.data.helper.listdata` that can be useful for working out how
much data is stored locally. It can be run using
'''

from heliopy.data import helper as heliohelper
heliohelper.listdata()

###############################################################################
# This will print a table with each probe and the total raw data stored
# along with the total *.hdf* file data stored
# (*.hdf* files are binary files that are much faster for python to read than
# raw data).
#
# Example output is:

'''
  Scanning files in /Users/dstansby/Data/
  ----------------------------------------
  |      Probe |        Raw |        HDF |
  |--------------------------------------|
  |        ace |    1.44 MB |  800.00  B |
  |    cluster |  200.39 MB |    0.00  B |
  |     helios |    2.37 GB |    1.41 GB |
  |        imp |   19.76 MB |   28.56 MB |
  |  messenger |   15.24 MB |   27.21 MB |
  |        mms |   70.11 MB |    0.00  B |
  |     themis |   64.31 MB |    0.00  B |
  |    ulysses |   54.78 MB |   47.98 MB |
  |       wind |  176.84 MB |   63.82 MB |
  |--------------------------------------|
  |--------------------------------------|
  |      Total |    2.96 GB |    1.57 GB |
  ----------------------------------------
'''
