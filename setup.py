from setuptools import setup

setup(name='pyspace',
      version='0.1',
      description='Python for Space Physics',
      url='https://github.com/dstansby/pyspace',
      author='David Stansby',
      author_email='dstansby@gmail.com',
      license='GPL-3.0',
      include_package_data=True,
      packages=['pyspace',
                'pyspace.data',
                'pyspace.plot',
                'pyspace.vector',
                'pyspace.util'],
      data_files=[('pyspace/data', ['pyspace/data/pyspacerc']),
                  ('pyspace', ['README.md'])])
