Creating a release
==================

1. Fetch the latest copy of the upstream repository

.. code-block:: bash

  git checkout master

2. Run

.. code-block:: bash

  git clean -xfd

to clean out any old builds

3. Tag the current version using the github releases page:
   https://github.com/heliopython/heliopy/releases

4. Fetch the newly created tag

.. code-block:: bash

  git fetch upstream
  git merge --ff-only upstream/master

5. Create a source distribution and a python wheel

.. code-block:: bash

  python setup.py sdist
  python setup.py bdist_wheel

6. Upload created wheels to pypi

.. code-block:: bash

  twine upload dist/*

See https://packaging.python.org/tutorials/distributing-packages/#packaging-your-project
for more information.

7. Update conda package at https://github.com/conda-forge/heliopy-feedstock
