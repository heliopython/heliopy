"""
Common space physics coordinate systems.

This submodule contains various space physics coordinate frames for use with
the `astropy.coordinates` module.
"""
import astropy.coordinates.baseframe as baseframe


class HeliocentricEarthEcliptic(baseframe.BaseCoordinateFrame):
    """
    A coordinate frame in the Heliocentric Earth Ecliptic (HEE) system.

    The x-y plane is the Earth mean ecliptic, and the x-axis points from the
    Sun to the Earth.
    """
