"""
heliopy

Open source python tools for space physics
"""
__version__ = '1.0.0'


def raise_import_error():
    raise ImportError(
        'HelioPy is no longer maintained or supported.\n'
        'Most functionality is now available elsewhere.\n'
        'See https://github.com/heliopython/heliopy/blob/main/README.md '
        'for more info.\n\n'
        'Downgrade to heliopy<1 to continue using the legacy code.')
