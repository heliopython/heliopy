from setuptools import setup
import os
import versioneer
import sys

if sys.version_info < (3, 6):
    sys.exit('Python versions older than 3.6 are not supported.')

# Config for read the docs
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if on_rtd:
    from distutils import dir_util
    ret = dir_util.copy_tree('examples/data',
                             '/home/docs/heliopy/data')
    print(ret)

setup(version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass())
