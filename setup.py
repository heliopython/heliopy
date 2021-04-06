import sys

from setuptools import setup

import versioneer

if sys.version_info < (3, 6):
    sys.exit('Python versions older than 3.6 are not supported.')

setup(version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass())
