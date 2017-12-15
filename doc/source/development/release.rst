Creating a release
==================

1. Fetch the latest copy of the upstream repository

.. code-block:: bash

  git fetch upstream
  git merge upstream/master


2. Run ``git clean -xfd`` to clean out any old builds
3. Tag the current version using

.. code-block:: bash

  git tag version-number
  git push
  git push --tags

4. Create a source distribution

.. code-block:: bash

  python setup.py sdist


5. Create a python wheel

.. code-block:: bash

  python setup.py bdist_wheel

6. Upload created wheels to pypi

.. code-block:: bash

  twine upload dist/*

See https://packaging.python.org/tutorials/distributing-packages/#packaging-your-project
for more information.
