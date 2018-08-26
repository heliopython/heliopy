Installing
==========

HelioPy is built on the Python programming language. The easiest way to install
Python with the various required scientific python modules is to use Anaconda.
Installation instructions can be found `here <https://docs.continuum.io/anaconda/install/>`_.

The minimum supported version of python is python 3.6.

Once you have a Python distribution installed, HelioPy can be installed using
either conda::

  conda install -c conda-forge heliopy

or pip::

  pip install heliopy

Module requirements
-------------------

Each module has a set of dependencies that are required for that module to
be used. To automatically install dependencies for a specific module, use
`pip install heliopy[modname]`, e.g. for the 'coordinates' module::

  pip install heliopy[coordinates]

Alternatively, to install all of the optional dependencies use::

  pip install heliopy[all]

In addition, there are the following optional requirements that add extra
functionality to HelioPy.

HDF file reader/writer
^^^^^^^^^^^^^^^^^^^^^^
Saving data to hdf files for quicker access requires the *PyTables* python
package. (see :ref:`sphx_glr_auto_examples_fast_file_loading.py`
for more information)

Installing from source
----------------------
The latest source code is available at
https://github.com/heliopython/heliopy/. To install from source follow these steps:

1. Install `git <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_
2. ``git clone https://github.com/heliopython/heliopy.git``
3. ``cd heliopy``
4. ``pip install .``

This will install HelioPy from source.
