from setuptools import setup

setup(name='heliopy',
      version='0.1',
      description='Python for Space Physics',
      url='https://github.com/dstansby/pyspace',
      author='David Stansby',
      author_email='dstansby@gmail.com',
      license='GPL-3.0',
      include_package_data=True,
      packages=['heliopy',
                'heliopy.data',
                'heliopy.plot',
                'heliopy.vector',
                'heliopy.util'],
      data_files=[('heliopy/data', ['heliopy/data/heliopyrc']),
                  ('heliopy', ['README.md'])])
