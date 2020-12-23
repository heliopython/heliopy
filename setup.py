from setuptools import setup
import os
import versioneer
import sys

if sys.version_info < (3, 6):
    sys.exit('Python versions older than 3.6 are not supported.')

setup(version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass())
