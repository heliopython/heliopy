"""
This submodule contains various space physics coordinate frames for use with
the :mod:`astropy.coordinates` module.
"""
import astropy.coordinates.baseframe as baseframe
import astropy.coordinates.representation as r
import astropy.coordinates as coords


class HeliocentricEarthEcliptic(baseframe.BaseCoordinateFrame):
    """
    A coordinate frame in the Heliocentric Earth Ecliptic (HEE) system.

    Possible call signatures::

        hee = HeliocentricEarthEcliptic(x, y, z)
        hee = HeliocentricEarthEcliptic(x, y, z, obstime=obstime)

    The x-y plane is the Earth mean ecliptic, the x-axis points from the
    Sun to the Earth, and the z-axis points North out of the ecliptic plane.

    Parameters
    ----------
    x : ~astropy.units.Quantity
        x-coordinate(s)
    y : ~astropy.units.Quantity
        y-coordinate(s)
    z : ~astropy.units.Quantity
        z-coordinate(s)
    obstime : datetime, optional
        Observation time. Required for some transformations between different
        coordinate systems.
    """
    name = 'HEE'
    default_representation = coords.CartesianRepresentation
    obstime = coords.TimeAttribute(default=None)


class GeocentricSolarEcliptic(baseframe.BaseCoordinateFrame):
    """
    A coordinate frame in the Geocentric Solar Ecliptic (GSE) system.

    Possible call signatures::

        gse = GeocentricSolarEcliptic(x, y, z)
        gse = GeocentricSolarEcliptic(x, y, z, obstime)

    The x-y plane is the Earth mean ecliptic, the x-axis points from the
    Earth to the Sun, and the z-axis points North out of the ecliptic plane.

    Parameters
    ----------
    x : ~astropy.units.Quantity
        x-coordinate(s)
    y : ~astropy.units.Quantity
        y-coordinate(s)
    z : ~astropy.units.Quantity
        z-coordinate(s)
    obstime : datetime, optional
        Observation time. Required for some transformations between different
        coordinate systems.
    """
    name = 'GSE'
    default_representation = coords.CartesianRepresentation
    obstime = coords.TimeAttribute(default=None)
