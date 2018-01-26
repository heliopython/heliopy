"""
Common space physics coordinate systems.

This submodule contains various space physics coordinate frames for use with
the :mod:`astropy.coordinates` module.
"""
import astropy.coordinates.baseframe as baseframe
import astropy.coordinates.representation as r
import astropy.coordinates as coords


class HeliocentricEarthEcliptic(baseframe.BaseCoordinateFrame):
    """
    A coordinate frame in the Heliocentric Earth Ecliptic (HEE) system.

    The x-y plane is the Earth mean ecliptic, the x-axis points from the
    Sun to the Earth, and the z-axis points North out of the ecliptic plane.
    """
    name = 'HEE'
    default_representation = coords.CartesianRepresentation
    obstime = coords.TimeAttribute(default=None)


class GeocentricSolarEcliptic(baseframe.BaseCoordinateFrame):
    """
    A coordinate frame in the Geocentric Solar Ecliptic (GSE) system.

    The x-y plane is the Earth mean ecliptic, the x-axis points from the
    Earth to the Sun, and the z-axis points North out of the ecliptic plane.
    """
    name = 'GSE'
    default_representation = coords.CartesianRepresentation
    obstime = coords.TimeAttribute(default=None)
