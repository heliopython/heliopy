Installing HelioPy
==================

HelioPy is built on the Python programming language. The easiest way to install
Python with the various required scientific python modules is to use Anaconda.
Installation instructions can be found `here <https://docs.continuum.io/anaconda/install/>`_.

Once you have a Python distribution installed, HelioPy can be installed using::

  pip install heliopy

Optional dependencies
---------------------

HDF file reader/writer
^^^^^^^^^^^^^^^^^^^^^^
Saving data to hdf files for quicker access requires PyTables.
(see :ref:`sphx_glr_auto_examples_fast_file_loading.py` for more information)

CDF Library
^^^^^^^^^^^
Reading in any data that is stored in .cdf files requires an installation of
the CDF library: https://cdf.gsfc.nasa.gov/

Installing from source
----------------------
The latest source code is available at
https://github.com/heliopython/heliopy/. To install from source follow these steps:

1. Install `git <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_
2. ``git clone https://github.com/heliopython/heliopy.git``
3. ``cd heliopy``
4. ``sudo pip install .``

This will install HelioPy from source and it's required dependancies.
