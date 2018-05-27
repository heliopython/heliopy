"""
This submodule contains various space physics coordinate frames for use with
the :mod:`astropy.coordinates` module.

.. warning::

  The functions in this submodule should never be called directly, transforming
  between coordinate frames should be done using
  :meth:`~astropy.coordinates.BaseCoordinateFrame.transform_to` on coordinate
  frame objects. See above for an example.
"""
import numpy as np

import astropy.coordinates.baseframe as baseframe
import astropy.coordinates.builtin_frames as astropy_frames
import astropy.coordinates.representation as r
import astropy.coordinates as coords
import astropy.units as u

import sunpy.coordinates.ephemeris as ephem


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


@coords.frame_transform_graph.transform(
    coords.AffineTransform,
    HeliocentricEarthEcliptic,
    GeocentricSolarEcliptic)
def hee_to_gse(hee_coord, gse_frame):
    '''
    Convert from HEE to GSE coordinates.
    '''
    obstime = hee_coord.obstime
    r_earth_sun = ephem.get_sunearth_distance(time=obstime)
    # Rotate 180deg around the z-axis
    R = np.array([[-1, 0, 0],
                  [0, -1, 0],
                  [0, 0, 1]])
    # Offset so centre is at Earth
    offset = coords.CartesianRepresentation(r_earth_sun, 0 * u.m, 0 * u.m)
    return R, offset


# TODO: re-enable this when a custom graph can be built
# __doc__ += astropy_frames._make_transform_graph_docs()
