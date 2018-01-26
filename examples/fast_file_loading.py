'''
Speeding up file import
=======================

For some files, reading in the original files can be very slow in Python.
heliopy has the option to automatically save files into the binary hdf
file format. Two copies of the data will be stored locally (original and hdf),
but will significantly speed up loading files.

To enable this option, make sure PyTables is installed using::

  pip install pytables

And then edit your heliopyrc file to enable hdf file saving
(see :doc:`/guide/configuring` for more information).

To check how much data is stored in both it's original format and hdf format
see :ref:`sphx_glr_auto_examples_data_inventory.py`.
'''
