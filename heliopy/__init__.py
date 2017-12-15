"""
heliopy

Open source python tools for space physics
"""

from heliopy.util.config import load_config
config = load_config()

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
