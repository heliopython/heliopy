Testing
=======

Running local tests
-------------------
To run tests locally, install pytest (https://docs.pytest.org/en/latest/).
Then from the :file:`heliopy` directory run::

  pytest

To run all tests apart from the ones that require data to be downloaded run::

   pytest -m "not data"

Continuous integration tests
----------------------------
To continuously check the codebase is working properly, tests are automatically
run every time a pull request is submitted or a pull request is merged.

Currently tests are run using these services:

- Linux: https://travis-ci.org/heliopython/heliopy
- Windows: https://ci.appveyor.com/
- Documentation: https://circleci.com/gh/heliopython/heliopy
