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
    from os import listdir
    ret = dir_util.copy_tree('examples/data',
                             '/home/docs/heliopy/data')
    print(ret)

setup(name='HelioPy',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Python for space physics',
      url='http://heliopy.org/',
      author='David Stansby',
      author_email='dstansby@gmail.com',
      license='GPL-3.0',
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'Natural Language :: English',
                   'Programming Language :: Python :: 3',
                   'Topic :: Scientific/Engineering :: Physics'],
      keywords='physics, space-physics',
      include_package_data=True,
      install_requires=['numpy',
                        'astropy'],
      extras_require={'spice': ['spiceypy'],
                      'data': ['pandas', 'sunpy', 'requests', 'cdflib',
                               'wget'],
                      'coordinates': ['sunpy']},
      python_requires='>=3.6',
      packages=['heliopy',
                'heliopy.coordinates',
                'heliopy.data',
                'heliopy.util'],
      package_data={'heliopy': ['heliopyrc']})
